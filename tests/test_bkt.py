"""Unit tests for Bayesian Knowledge Tracing update behavior."""

from __future__ import annotations

import math

from backend.api.schemas import SkillMastery
from backend.engine.bkt import BKTModel


def test_posterior_update_formula_known_values() -> None:
	model = BKTModel(p_s=0.10, p_g=0.20)
	skill = SkillMastery(
		esco_uri="esco:python",
		label="Python",
		p_m=0.60,
		p_l0=0.60,
		ci_lower=0.0,
		ci_upper=1.0,
		ci_color="red",
		evidence="python",
	)

	matrix = model.initialize([skill])
	updated = model.posterior_update(matrix, module_id="m1", correct=True)
	p_l = 0.60
	p_s = 0.10
	p_g = 0.20
	p_t = 0.35

	posterior = (p_l * (1 - p_s)) / ((p_l * (1 - p_s)) + ((1 - p_l) * p_g))
	expected = posterior + (1 - posterior) * p_t

	assert math.isclose(updated["esco:python"]["p_m"], expected, rel_tol=1e-9)
	assert 0.0 <= updated["esco:python"]["ci_lower"] <= updated["esco:python"]["ci_upper"] <= 1.0
	assert updated["esco:python"]["ci_color"] in {"green", "amber", "red"}
