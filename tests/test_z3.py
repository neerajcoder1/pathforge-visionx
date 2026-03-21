"""Formal verification tests for all required Z3 rule checks."""

from __future__ import annotations

import networkx as nx

from backend.engine.z3_verifier import verify_path


def _base_graph() -> nx.DiGraph:
	g = nx.DiGraph()
	g.add_edge("skill:sql", "skill:python", relation="PREREQUISITE_OF")
	g.graph["mandatory_modules"] = {"M_MANDATORY"}
	g.graph["catalog_courses"] = [{"course_id": "M_MANDATORY", "is_mandatory": True}]
	return g


def test_verify_path_pass_case() -> None:
	g = _base_graph()
	path = [
		{
			"course_id": "M_MANDATORY",
			"teaches": ["skill:sql", "skill:python"],
			"prerequisite_mastery": {"skill:sql": 0.90},
			"is_mandatory": True,
		}
	]
	result = verify_path(path, {"M_MANDATORY"}, g)
	assert result["result"] == "PASS"


def test_verify_path_rule1_catalog_membership_fail() -> None:
	g = _base_graph()
	path = [{"course_id": "M_UNKNOWN", "teaches": ["skill:python"], "prerequisite_mastery": {}}]
	result = verify_path(path, {"M_MANDATORY"}, g)
	assert result["result"] == "FAIL"
	assert result["violated_rule"] == "CATALOG_MEMBERSHIP"


def test_verify_path_rule2_prerequisite_satisfied_fail() -> None:
	g = _base_graph()
	path = [
		{
			"course_id": "M_MANDATORY",
			"teaches": ["skill:python"],
			"prerequisite_mastery": {"skill:sql": 0.80},
			"is_mandatory": True,
		}
	]
	result = verify_path(path, {"M_MANDATORY"}, g)
	assert result["result"] == "FAIL"
	assert result["violated_rule"] == "PREREQUISITE_SATISFIED"


def test_verify_path_rule3_no_cycles_fail() -> None:
	g = nx.DiGraph()
	g.add_edge("A", "B", relation="PREREQUISITE_OF")
	g.add_edge("B", "A", relation="PREREQUISITE_OF")
	g.graph["mandatory_modules"] = set()
	path = [{"course_id": "M1", "teaches": ["A", "B"], "prerequisite_mastery": {"A": 0.9}}]
	result = verify_path(path, {"M1"}, g)
	assert result["result"] == "FAIL"
	assert result["violated_rule"] == "NO_CYCLES"


def test_verify_path_rule4_compliance_mandatory_fail() -> None:
	g = nx.DiGraph()
	g.graph["mandatory_modules"] = {"M_MANDATORY"}
	path = [{"course_id": "M_OPTIONAL", "teaches": ["skill:x"], "prerequisite_mastery": {}}]
	result = verify_path(path, {"M_OPTIONAL", "M_MANDATORY"}, g)
	assert result["result"] == "FAIL"
	assert result["violated_rule"] == "COMPLIANCE_MANDATORY"
