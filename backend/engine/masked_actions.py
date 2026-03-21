"""Eligibility masking over course actions using prerequisite mastery."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

import networkx as nx


def _get_value(course: Any, key: str, default: Any = None) -> Any:
	if isinstance(course, dict):
		return course.get(key, default)
	return getattr(course, key, default)


def _required_skills(course: Any, graph: nx.DiGraph) -> list[str]:
	explicit = _get_value(course, "requires", None)
	if explicit:
		return list(explicit)

	teaches = _get_value(course, "teaches", []) or []
	required: set[str] = set()
	for skill in teaches:
		for pred in graph.predecessors(skill):
			edge_data = graph.get_edge_data(pred, skill, default={})
			relation = str(edge_data.get("relation", "")).upper()
			if relation == "PREREQUISITE_OF":
				required.add(pred)
	return sorted(required)


def compute_eligible_set(mastery_matrix: Dict[str, dict], graph: nx.DiGraph, all_courses: List[Any]) -> List[Any]:
	"""Filter out any course where at least one prerequisite has P(M) < 0.85."""
	eligible: list[Any] = []
	for course in all_courses:
		prerequisites = _required_skills(course, graph)
		allowed = True
		for req_skill in prerequisites:
			row = mastery_matrix.get(req_skill, {})
			p_m = float(row.get("p_m", 0.0))
			if p_m < 0.85:
				allowed = False
				break
		if allowed:
			eligible.append(course)
	return eligible
