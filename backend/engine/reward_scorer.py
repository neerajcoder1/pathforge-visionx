"""Module reward scoring for adaptive path planning."""

from __future__ import annotations

from typing import Any, Dict, List

import networkx as nx
import numpy as np

ScoredModule = Dict[str, Any]


def _get_value(course: Any, key: str, default: Any = None) -> Any:
	if isinstance(course, dict):
		return course.get(key, default)
	return getattr(course, key, default)


def _course_to_dict(course: Any) -> dict:
	if isinstance(course, dict):
		return dict(course)
	data = {}
	for key in ["course_id", "title", "hours", "teaches", "is_mandatory", "requires"]:
		data[key] = _get_value(course, key)
	return data


def score_modules(
	eligible_set: List[Any],
	mastery_matrix: Dict[str, dict],
	graph: nx.DiGraph,
	lambda_vals: List[float] = [2.0, 1.0, 0.2],
) -> Dict[float, List[ScoredModule]]:
	"""Score modules using vectorized reward computation for all lambda values."""
	if not eligible_set:
		return {float(l): [] for l in lambda_vals}

	courses = [_course_to_dict(c) for c in eligible_set]
	n_courses = len(courses)
	lambdas = np.array(lambda_vals, dtype=float)

	estimated_time = np.array([float(c.get("hours", 0.0) or 0.0) for c in courses], dtype=float)
	benefit = np.zeros(n_courses, dtype=float)

	for idx, course in enumerate(courses):
		teaches = course.get("teaches", []) or []
		total = 0.0
		for skill in teaches:
			p_m = float(mastery_matrix.get(skill, {}).get("p_m", 0.2))
			delta = max(0.0, (1.0 - p_m) * 0.2)
			criticality = float(graph.nodes.get(skill, {}).get("criticality", 1.0))
			total += delta * criticality
		benefit[idx] = total

	# Single vectorized pass: reward matrix shape = [n_lambda, n_courses]
	reward_matrix = benefit[np.newaxis, :] - lambdas[:, np.newaxis] * estimated_time[np.newaxis, :]

	scored_by_lambda: Dict[float, List[ScoredModule]] = {}
	for l_idx, lambda_val in enumerate(lambdas.tolist()):
		order = np.argsort(-reward_matrix[l_idx])
		scored: list[ScoredModule] = []
		for c_idx in order.tolist():
			course = dict(courses[c_idx])
			course["reward_score"] = float(reward_matrix[l_idx, c_idx])
			course["bkt_delta"] = float(benefit[c_idx])
			scored.append(course)
		scored_by_lambda[float(lambda_val)] = scored

	return scored_by_lambda
