"""Formal path verification using Z3 and graph constraints."""

from __future__ import annotations

from typing import Any, Dict, List, Set

import networkx as nx
from z3 import BoolVal, Solver, sat


def _get_value(item: Any, key: str, default: Any = None) -> Any:
	if isinstance(item, dict):
		return item.get(key, default)
	return getattr(item, key, default)


def _fail(rule: str, module: str) -> Dict[str, str]:
	return {"result": "FAIL", "violated_rule": rule, "violating_module": module}


def verify_path(path: List[Any], catalog_ids: Set[str], graph: nx.DiGraph) -> Dict[str, str]:
	"""Verify a candidate curriculum path against required formal rules."""
	solver = Solver()

	# Rule 1: CATALOG_MEMBERSHIP
	for module in path:
		module_id = str(_get_value(module, "course_id", ""))
		in_catalog = module_id in catalog_ids
		solver.push()
		solver.add(BoolVal(in_catalog))
		if solver.check() != sat:
			solver.pop()
			return _fail("CATALOG_MEMBERSHIP", module_id)
		solver.pop()
		if not in_catalog:
			return _fail("CATALOG_MEMBERSHIP", module_id)

	# Rule 2: PREREQUISITE_SATISFIED (P(M) > 0.85)
	for module in path:
		module_id = str(_get_value(module, "course_id", ""))
		prereq_mastery = _get_value(module, "prerequisite_mastery", {}) or {}
		for _, p_m in prereq_mastery.items():
			if float(p_m) <= 0.85:
				return _fail("PREREQUISITE_SATISFIED", module_id)

	# Rule 3: NO_CYCLES over prerequisite subgraph induced by path taught skills.
	skill_nodes: set[str] = set()
	for module in path:
		skill_nodes.update(_get_value(module, "teaches", []) or [])

	sub = nx.DiGraph()
	for node in skill_nodes:
		sub.add_node(node)
	for u, v, data in graph.edges(data=True):
		if u in skill_nodes and v in skill_nodes:
			relation = str(data.get("relation", "")).upper()
			if relation == "PREREQUISITE_OF":
				sub.add_edge(u, v)
	try:
		list(nx.topological_sort(sub))
	except nx.NetworkXUnfeasible:
		violating = str(_get_value(path[0], "course_id", "unknown")) if path else "unknown"
		return _fail("NO_CYCLES", violating)

	# Rule 4: COMPLIANCE_MANDATORY
	mandatory_ids = set(graph.graph.get("mandatory_modules", set()))
	catalog_courses = graph.graph.get("catalog_courses", [])
	for c in catalog_courses:
		if bool(_get_value(c, "is_mandatory", False)):
			mandatory_ids.add(str(_get_value(c, "course_id", "")))

	path_ids = {str(_get_value(m, "course_id", "")) for m in path}
	for mandatory in sorted(mandatory_ids):
		if mandatory and mandatory not in path_ids:
			return _fail("COMPLIANCE_MANDATORY", mandatory)

	return {"result": "PASS", "violated_rule": "", "violating_module": ""}
