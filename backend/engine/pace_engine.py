"""PACE orchestration engine for adaptive curriculum generation."""

from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence, Set

import networkx as nx
from groq import Groq
from rapidfuzz import fuzz, process

from backend.api.schemas import CourseModule, PaceResult, PathVariant, SkillMastery
from backend.engine.bkt import BKTModel
from backend.engine.masked_actions import compute_eligible_set
from backend.engine.reward_scorer import score_modules
from backend.engine.z3_verifier import verify_path
from backend.extraction.entity_linker import link_to_esco
from backend.extraction.extractor import extract_skills
from backend.trace.justifier import render_justifications
from backend.trace.ledger import write_ledger


FUZZY_MATCH_THRESHOLD = 78


def _decompose_jd_skills(jd_text: str) -> list[str]:
	timeout_s = float(os.getenv("GROQ_TIMEOUT_SECONDS", "2"))
	api_key = os.getenv("GROQ_API_KEY")
	if api_key:
		try:
			client = Groq(api_key=api_key, timeout=timeout_s)
			completion = client.chat.completions.create(
				model="qwen-2.5-7b",
				temperature=0,
				messages=[
					{
						"role": "system",
						"content": "Extract core skill phrases from this job description as a comma-separated list.",
					},
					{"role": "user", "content": jd_text[:12000]},
				],
			)
			content = completion.choices[0].message.content or ""
			raw_skills = [s.strip().lower() for s in content.split(",") if s.strip()]
			if raw_skills:
				return raw_skills
		except Exception:
			pass

	tokens = re.findall(r"[a-zA-Z][a-zA-Z+\-]{2,}", jd_text.lower())
	stop = {"with", "and", "for", "the", "you", "our", "your", "role", "team"}
	skills: list[str] = []
	for t in tokens:
		if t not in stop and t not in skills:
			skills.append(t)
		if len(skills) >= 12:
			break
	return skills


def _map_jd_tokens_to_uris(tokens: Sequence[str], alias_table: Dict[str, str]) -> list[str]:
	"""Map JD tokens to ESCO URIs using fuzzy matching with a conservative threshold."""
	normalized_aliases = {str(k).strip().lower(): str(v).strip() for k, v in (alias_table or {}).items() if str(k).strip()}
	resolved: list[str] = []
	choices = list(normalized_aliases.keys())
	for token in tokens:
		norm = token.strip().lower()
		if not norm:
			continue
		if norm in normalized_aliases:
			resolved.append(normalized_aliases[norm])
			continue
		if choices:
			best = process.extractOne(norm, choices, scorer=fuzz.WRatio)
			if best and best[1] >= FUZZY_MATCH_THRESHOLD:
				resolved.append(normalized_aliases.get(best[0], norm))
	if not resolved:
		return [normalized_aliases.get(t.strip().lower(), t.strip().lower()) for t in tokens if t.strip()]
	# Preserve order while removing duplicates.
	seen: set[str] = set()
	ordered: list[str] = []
	for uri in resolved:
		if uri and uri not in seen:
			seen.add(uri)
			ordered.append(uri)
	return ordered


def _mastery_to_schema(matrix: Dict[str, dict]) -> list[SkillMastery]:
	items: list[SkillMastery] = []
	for skill_id, row in matrix.items():
		if skill_id.startswith("_"):
			continue
		p_m = float(row.get("p_m", 0.2))
		p_l0 = float(row.get("p_l0", p_m))
		ci_lower = float(row.get("ci_lower", 0.0))
		ci_upper = float(row.get("ci_upper", 1.0))
		items.append(
			SkillMastery(
				esco_uri=skill_id,
				label=str(row.get("label", skill_id)),
				p_m=p_m,
				p_l0=p_l0,
				ci_lower=max(0.0, min(1.0, ci_lower)),
				ci_upper=max(max(0.0, min(1.0, ci_upper)), max(0.0, min(1.0, ci_lower))),
				ci_color=str(row.get("ci_color") or "green"),
				evidence=str(row.get("evidence") or "Extracted from text"),
			)
		)
	return items


def _infer_similar_transfer(matrix: Dict[str, dict], graph: nx.DiGraph) -> None:
	for src, dst, data in graph.edges(data=True):
		relation = str(data.get("relation", "")).upper()
		if relation != "SIMILAR_TO":
			continue
		src_p = float(matrix.get(src, {}).get("p_m", 0.0))
		if src_p > 0.75:
			weight = float(data.get("similarity_weight", 0.8))
			inferred = max(0.0, min(1.0, src_p * weight))
			if dst not in matrix:
				matrix[dst] = {
					"esco_uri": dst,
					"label": str(graph.nodes.get(dst, {}).get("label", dst)),
					"p_l0": inferred,
					"p_m": inferred,
					"ci_lower": max(0.0, inferred - 0.2),
					"ci_upper": min(1.0, inferred + 0.2),
					"ci_color": "amber",
					"effective_evidence_count": 1,
					"evidence": "similarity_transfer",
				}
			else:
				matrix[dst]["p_m"] = max(float(matrix[dst].get("p_m", 0.0)), inferred)


def _gap_discovery(jd_skill_uris: Sequence[str], matrix: Dict[str, dict], graph: nx.DiGraph) -> set[str]:
	gaps: set[str] = set()
	for target in jd_skill_uris:
		if float(matrix.get(target, {}).get("p_m", 0.0)) < 0.85:
			gaps.add(target)
		if target in graph:
			for upstream in nx.bfs_tree(graph.reverse(copy=False), source=target, depth_limit=2).nodes:
				if float(matrix.get(upstream, {}).get("p_m", 0.0)) < 0.85:
					gaps.add(upstream)
	return gaps


def _course_from_scored(scored: dict) -> CourseModule:
	return CourseModule(
		course_id=str(scored.get("course_id", "")),
		title=str(scored.get("title", "")),
		hours=float(scored.get("hours", 0.0) or 0.0),
		teaches=list(scored.get("teaches", []) or []),
		is_mandatory=bool(scored.get("is_mandatory", False)),
		bkt_delta=float(scored.get("bkt_delta", 0.0) or 0.0),
		reward_score=float(scored.get("reward_score", 0.0) or 0.0),
		justification_en="",
		z3_result="PASS",
		rejection_reason=None,
	)


def _compute_cvs(path: list[CourseModule], target_skills: set[str]) -> float:
	if not path:
		return 0.0
	taught = {s for m in path for s in m.teaches}
	coverage = (len(taught & target_skills) / max(1, len(target_skills)))
	total_hours = sum(m.hours for m in path)
	return float(max(0.0, min(1.0, 0.7 * coverage + 0.3 * (1.0 / (1.0 + total_hours / 40.0)))))


def _skill_name(item: Any) -> str:
	if isinstance(item, dict):
		return str(item.get("name") or item.get("mention") or item.get("label") or item)
	return str(getattr(item, "name", getattr(item, "mention", getattr(item, "label", item))))


def _build_target_mastery(
	target_skill_ids: set[str],
	matrix: Dict[str, dict],
	graph: nx.DiGraph,
) -> list[SkillMastery]:
	"""Build target skill rows from JD/gap set directly, even when current mastery is sparse."""
	rows: list[SkillMastery] = []
	for skill_id in sorted(target_skill_ids):
		row = matrix.get(skill_id, {})
		node = graph.nodes.get(skill_id, {}) if skill_id in graph else {}
		label = str(node.get("label", row.get("label", skill_id)))
		p_m = float(row.get("p_m", 0.0))
		ci_lower = float(row.get("ci_lower", max(0.0, p_m - 0.2)))
		ci_upper = float(row.get("ci_upper", min(1.0, p_m + 0.2)))
		rows.append(
			SkillMastery(
				esco_uri=skill_id,
				label=label,
				p_m=p_m,
				p_l0=float(row.get("p_l0", p_m)),
				ci_lower=max(0.0, min(1.0, ci_lower)),
				ci_upper=max(max(0.0, min(1.0, ci_upper)), max(0.0, min(1.0, ci_lower))),
				ci_color=str(row.get("ci_color") or "green"),
				evidence=str(row.get("evidence") or "Extracted from text"),
			)
		)
	return rows


def _fallback_linked_skills_from_resume(
	resume_text: str,
	alias_table: Dict[str, str],
	graph: nx.DiGraph,
) -> list[SkillMastery]:
	"""Derive a weak prior from resume text when extractor output is empty."""
	resume_tokens = _decompose_jd_skills(resume_text)
	if not resume_tokens:
		return []

	resolved_uris = _map_jd_tokens_to_uris(resume_tokens, alias_table)
	fallback_ids = list(dict.fromkeys(resolved_uris or resume_tokens))
	seed: list[SkillMastery] = []
	for skill_id in fallback_ids[:30]:
		node = graph.nodes.get(skill_id, {}) if skill_id in graph else {}
		label = str(node.get("label", skill_id))
		seed.append(
			SkillMastery(
				esco_uri=skill_id,
				label=label,
				p_m=0.20,
				p_l0=0.20,
				ci_lower=0.0,
				ci_upper=0.4,
				ci_color="green",
				evidence="Extracted from text",
			)
		)
	return seed


def run_pace(resume_text: str, jd_text: str, graph: nx.DiGraph, db_conn: Any) -> PaceResult:
	"""Run end-to-end PACE pipeline and return a complete schema-validated result."""
	session_id = str(uuid.uuid4())

	# a) Resume skill extraction
	mentions = extract_skills(resume_text)
	print(f"Extracted Resume Skills: [{', '.join(_skill_name(s) for s in mentions)}]", flush=True)

	# b) ESCO linking
	alias_table = graph.graph.get("alias_table", {})
	linked_skills = link_to_esco(mentions, graph, alias_table)
	if not linked_skills:
		linked_skills = _fallback_linked_skills_from_resume(resume_text, alias_table, graph)
	print(f"Linked Resume Skills Count: {len(linked_skills)}", flush=True)

	# c) BKT initialization
	bkt = BKTModel()
	matrix = bkt.initialize(linked_skills)

	# d) JD extraction (directly from jd_text), then decomposition fallback if empty
	jd_mentions = extract_skills(jd_text)
	jd_tokens = [str(getattr(m, "mention", "")).strip().lower() for m in jd_mentions if str(getattr(m, "mention", "")).strip()]
	if not jd_tokens:
		jd_tokens = _decompose_jd_skills(jd_text)
	print(f"Extracted JD Skills: [{', '.join(jd_tokens)}]", flush=True)
	jd_skill_uris = _map_jd_tokens_to_uris(jd_tokens, alias_table)

	# e) Gap discovery via upstream BFS
	target_gap_set = _gap_discovery(jd_skill_uris, matrix, graph)

	# f) SIMILAR_TO transfer
	_infer_similar_transfer(matrix, graph)

	# g) Eligibility set
	all_courses = graph.graph.get("catalog_courses", [])
	eligible_set = compute_eligible_set(matrix, graph, all_courses)

	# h) Score modules in one vectorized pass
	scored = score_modules(eligible_set, matrix, graph, lambda_vals=[2.0, 1.0, 0.2])

	# i,j) Build path variants and verify with replanning on failure
	labels = {2.0: "Speed", 1.0: "Balance", 0.2: "Depth"}
	catalog_ids = {str(c.get("course_id", "")) if isinstance(c, dict) else str(getattr(c, "course_id", "")) for c in all_courses}
	variants: list[PathVariant] = []
	ledger_entries: list[dict] = []

	for lambda_val in [2.0, 1.0, 0.2]:
		ranked = scored.get(lambda_val, [])[:8]
		path_modules = [_course_from_scored(item) for item in ranked]

		verify = verify_path([m.model_dump() for m in path_modules], catalog_ids, graph)
		if verify.get("result") == "FAIL":
			violating = verify.get("violating_module", "")
			path_modules = [m for m in path_modules if m.course_id != violating]
			verify = verify_path([m.model_dump() for m in path_modules], catalog_ids, graph)

		total_hours = sum(m.hours for m in path_modules)
		target_skills = set(target_gap_set or jd_skill_uris)
		coverage = len({s for m in path_modules for s in m.teaches} & target_skills) / max(1, len(target_skills))
		cvs = _compute_cvs(path_modules, target_skills)

		for m in path_modules:
			m.z3_result = verify.get("result", "FAIL")
			if m.z3_result == "FAIL":
				m.rejection_reason = verify.get("violated_rule")

			ledger_entries.append(
				{
					"_db_conn": db_conn,
					"step_id": f"score-{labels[lambda_val].lower()}-{m.course_id}",
					"timestamp": datetime.now(timezone.utc).isoformat(),
					"input_mastery_snapshot": {k: v.get("p_m") for k, v in matrix.items() if not k.startswith("_")},
					"action_module_id": m.course_id,
					"bkt_delta_per_skill": {s: m.bkt_delta / max(1, len(m.teaches)) for s in m.teaches},
					"criticality_scores": {s: graph.nodes.get(s, {}).get("criticality", 1.0) for s in m.teaches},
					"prerequisite_chain": list(getattr(m, "teaches", [])),
					"z3_result": verify,
					"rejection_reason": None if verify.get("result") == "PASS" else verify.get("violated_rule"),
				}
			)

		variants.append(
			PathVariant(
				label=labels[lambda_val],
				lambda_val=lambda_val,
				modules=path_modules,
				total_hours=float(total_hours),
				cvs=float(cvs),
				skill_coverage_pct=float(coverage * 100.0),
				z3_verified=verify.get("result") == "PASS",
			)
		)

	# k) CVS baseline against legacy alphabetical catalog sequence
	legacy_courses = sorted(
		[_course_from_scored(c if isinstance(c, dict) else c.__dict__) for c in all_courses],
		key=lambda x: x.course_id,
	)
	target_skills = set(target_gap_set or jd_skill_uris)
	cvs_nexus = float(max(v.cvs for v in variants) if variants else 0.0)
	cvs_legacy = _compute_cvs(legacy_courses, target_skills)

	# l) Ledger persistence
	ledger = write_ledger(session_id, ledger_entries)

	# m) Justifications
	justifications = render_justifications(ledger)
	just_iter = iter(justifications)
	for variant in variants:
		for module in variant.modules:
			module.justification_en = next(just_iter, "Selected to maximize mastery gain under constraints.")

	# n) Return complete PaceResult
	current_mastery = _mastery_to_schema(matrix)
	target_mastery = _build_target_mastery(target_skills, matrix, graph) if target_skills else []
	return PaceResult(
		session_id=session_id,
		current_mastery=current_mastery,
		target_skills=target_mastery,
		path_variants=variants,
		cvs_nexus=float(cvs_nexus),
		cvs_legacy=float(cvs_legacy),
		decision_ledger=ledger,
		diagnostic_required=any(not v.z3_verified for v in variants),
	)
