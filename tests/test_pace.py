"""Golden-flow tests for PACE engine orchestration output schema."""

from __future__ import annotations

import networkx as nx

from backend.api.schemas import PaceResult
from backend.engine.pace_engine import run_pace


def _graph_fixture() -> nx.DiGraph:
	g = nx.DiGraph()
	g.add_node("esco:python", label="Python", criticality=1.0)
	g.add_node("esco:sql", label="SQL", criticality=1.2)
	g.add_node("esco:communication", label="Communication", criticality=0.8)

	g.add_edge("esco:sql", "esco:python", relation="PREREQUISITE_OF")
	g.add_edge("esco:python", "esco:communication", relation="SIMILAR_TO", similarity_weight=0.6)

	g.graph["alias_table"] = {
		"python": "esco:python",
		"sql": "esco:sql",
		"communication": "esco:communication",
	}
	g.graph["mandatory_modules"] = {"M_FOUNDATION"}
	g.graph["catalog_courses"] = [
		{
			"course_id": "M_FOUNDATION",
			"title": "Foundation",
			"hours": 6.0,
			"teaches": ["esco:sql"],
			"requires": [],
			"is_mandatory": True,
		},
		{
			"course_id": "M_PYTHON",
			"title": "Python Applied",
			"hours": 8.0,
			"teaches": ["esco:python"],
			"requires": ["esco:sql"],
			"is_mandatory": False,
		},
		{
			"course_id": "M_COMM",
			"title": "Communication",
			"hours": 3.0,
			"teaches": ["esco:communication"],
			"requires": [],
			"is_mandatory": False,
		},
	]
	return g


def test_run_pace_golden_case_one() -> None:
	result = run_pace(
		resume_text="Built Python pipelines and developed SQL dashboards.",
		jd_text="Need Python SQL communication skills.",
		graph=_graph_fixture(),
		db_conn=None,
	)
	assert isinstance(result, PaceResult)
	assert len(result.path_variants) == 3


def test_run_pace_golden_case_two() -> None:
	result = run_pace(
		resume_text="Familiar with SQL and learning Python.",
		jd_text="Role needs SQL and Python basics.",
		graph=_graph_fixture(),
		db_conn=None,
	)
	dumped = result.model_dump()
	assert "decision_ledger" in dumped
	assert isinstance(dumped["path_variants"], list)


def test_run_pace_golden_case_three() -> None:
	result = run_pace(
		resume_text="Experienced in communication and project work.",
		jd_text="Looking for communication and python.",
		graph=_graph_fixture(),
		db_conn=None,
	)
	assert result.cvs_nexus >= 0.0
	assert result.cvs_legacy >= 0.0
