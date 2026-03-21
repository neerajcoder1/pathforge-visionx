"""Bayesian Knowledge Tracing model for mastery updates."""

from __future__ import annotations

import math
from typing import Any, Dict, List

from backend.api.schemas import SkillMastery

MasteryRow = Dict[str, Any]
MasteryMatrix = Dict[str, MasteryRow]


class BKTModel:
	"""BKT implementation with configurable guess/slip/transition parameters."""

	def __init__(self, p_s: float = 0.10, p_g: float = 0.20) -> None:
		self.p_s = p_s
		self.p_g = p_g

	@staticmethod
	def _transition_probability(level: str) -> float:
		return 0.15 if level == "advanced" else 0.35

	@staticmethod
	def _ci_color(ci_lower: float, ci_upper: float) -> str:
		width = ci_upper - ci_lower
		if width < 0.15:
			return "green"
		if width <= 0.30:
			return "amber"
		return "red"

	@staticmethod
	def _confidence_interval(p_m: float, n: int) -> tuple[float, float, str]:
		n_eff = max(1, n)
		margin = 1.96 * math.sqrt(max(0.0, p_m * (1 - p_m) / n_eff))
		lower = max(0.0, p_m - margin)
		upper = min(1.0, p_m + margin)
		return lower, upper, BKTModel._ci_color(lower, upper)

	def initialize(self, skill_entities: List[SkillMastery]) -> MasteryMatrix:
		"""Create a mastery matrix keyed by ESCO URI."""
		matrix: MasteryMatrix = {}
		for skill in skill_entities:
			row: MasteryRow = {
				"esco_uri": skill.esco_uri,
				"label": skill.label,
				"p_m": float(skill.p_m),
				"p_l0": float(skill.p_l0),
				"level": "foundational",
				"effective_evidence_count": 1,
				"evidence": skill.evidence,
			}
			ci_l, ci_u, ci_c = self._confidence_interval(row["p_m"], row["effective_evidence_count"])
			row["ci_lower"] = ci_l
			row["ci_upper"] = ci_u
			row["ci_color"] = ci_c
			matrix[skill.esco_uri] = row
		return matrix

	def posterior_update(self, matrix: MasteryMatrix, module_id: str, correct: bool) -> MasteryMatrix:
		"""Update mastery posteriors for skills associated with a learning module.

		Required formula (correct response):
		P(L|correct) = P(L)*(1-P(S)) / [P(L)*(1-P(S)) + (1-P(L))*P(G)]
		"""
		module_skill_map = matrix.get("_module_skill_map", {})
		skill_ids = module_skill_map.get(module_id, [k for k in matrix.keys() if not k.startswith("_")])

		for skill_id in skill_ids:
			if skill_id not in matrix:
				continue
			row = matrix[skill_id]
			p_l = float(row.get("p_m", 0.2))
			p_t = self._transition_probability(str(row.get("level", "foundational")))

			if correct:
				denom = (p_l * (1 - self.p_s)) + ((1 - p_l) * self.p_g)
				posterior = (p_l * (1 - self.p_s)) / denom if denom else p_l
			else:
				denom = (p_l * self.p_s) + ((1 - p_l) * (1 - self.p_g))
				posterior = (p_l * self.p_s) / denom if denom else p_l

			updated = posterior + (1 - posterior) * p_t
			updated = float(max(0.0, min(1.0, updated)))

			row["p_m"] = updated
			row["effective_evidence_count"] = int(row.get("effective_evidence_count", 1)) + 1
			ci_l, ci_u, ci_c = self._confidence_interval(updated, row["effective_evidence_count"])
			row["ci_lower"] = ci_l
			row["ci_upper"] = ci_u
			row["ci_color"] = ci_c

		return matrix
