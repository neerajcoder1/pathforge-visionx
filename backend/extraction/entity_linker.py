"""Entity linking from extracted mentions to ESCO skills."""

from __future__ import annotations

import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

import networkx as nx
from rapidfuzz import fuzz, process

from backend.api.schemas import SkillMastery


PROFICIENCY_PRIORS = {
	"high": 0.90,
	"mid": 0.70,
	"low": 0.40,
	"none": 0.20,
}

HIGH_TERMS = {"architected", "led", "designed", "expert", "principal"}
MID_TERMS = {"built", "developed", "proficient", "experienced", "senior"}
LOW_TERMS = {"familiar", "basic", "exposure", "learning"}


def _normalize(text: str) -> str:
	return re.sub(r"\s+", " ", (text or "").strip().lower())


def _proficiency_prior(signal: str) -> float:
	s = _normalize(signal)
	if any(term in s for term in HIGH_TERMS):
		return PROFICIENCY_PRIORS["high"]
	if any(term in s for term in MID_TERMS):
		return PROFICIENCY_PRIORS["mid"]
	if any(term in s for term in LOW_TERMS):
		return PROFICIENCY_PRIORS["low"]
	return PROFICIENCY_PRIORS["none"]


def _apply_recency(prior: float, years_since_use: float) -> float:
	return float(max(0.0, min(1.0, prior * math.exp(-0.15 * max(0.0, years_since_use)))))


def _ann_lookup(graph: nx.DiGraph, mention: str) -> Optional[str]:
	# Hook for pgvector ANN fallback provided by orchestration layer.
	ann_fn = graph.graph.get("ann_lookup")
	if callable(ann_fn):
		try:
			result = ann_fn(mention)
			if isinstance(result, str) and result:
				return result
		except Exception:
			return None
	return None


def _resolve_uri(mention: str, alias_table: Dict[str, str], graph: nx.DiGraph) -> Optional[str]:
	normalized = _normalize(mention)
	if not normalized:
		return None
	if normalized in alias_table:
		return alias_table[normalized]

	choices = list(alias_table.keys())
	if choices:
		best = process.extractOne(normalized, choices, scorer=fuzz.WRatio)
		if best and best[1] >= 85:
			return alias_table.get(best[0])

	# pgvector ANN fallback hook.
	return _ann_lookup(graph, mention)


def link_to_esco(mentions: List[Any], graph: nx.DiGraph, alias_table: dict) -> List[SkillMastery]:
	"""Map extracted mentions to ESCO nodes and compute initial mastery priors."""
	linked: list[SkillMastery] = []
	for mention_obj in mentions:
		mention = str(getattr(mention_obj, "mention", "") or "")
		signal = str(getattr(mention_obj, "proficiency_signal", "") or "")
		implied_years = float(getattr(mention_obj, "implied_years", 0.0) or 0.0)

		esco_uri = _resolve_uri(mention, alias_table, graph)
		if not esco_uri:
			continue

		prior = _proficiency_prior(signal)
		p_l0 = _apply_recency(prior, years_since_use=implied_years)

		node_data = graph.nodes.get(esco_uri, {})
		label = str(node_data.get("label", mention))

		# Start with broad CI; BKT initialization updates this with evidence counts.
		ci_half = 0.20
		linked.append(
			SkillMastery(
				esco_uri=esco_uri,
				label=label,
				p_m=p_l0,
				p_l0=p_l0,
				ci_lower=max(0.0, p_l0 - ci_half),
				ci_upper=min(1.0, p_l0 + ci_half),
				ci_color="amber",
				evidence=mention,
			)
		)

	return linked
