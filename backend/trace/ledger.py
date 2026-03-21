"""Decision ledger persistence for PACE orchestration traces."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def write_ledger(session_id: str, entries: List[Dict[str, Any]]) -> dict:
	"""Persist and return decision ledger data.

	If an entry includes `_db_conn`, a best-effort insert into `decision_ledger`
	is attempted. This keeps the function usable in local/test contexts.
	"""
	normalized: list[dict] = []
	db_conn = None
	for e in entries:
		if db_conn is None and "_db_conn" in e:
			db_conn = e.get("_db_conn")

		normalized.append(
			{
				"step_id": str(e.get("step_id", "")),
				"timestamp": str(e.get("timestamp") or datetime.now(timezone.utc).isoformat()),
				"input_mastery_snapshot": e.get("input_mastery_snapshot", {}),
				"action_module_id": str(e.get("action_module_id", "")),
				"bkt_delta_per_skill": e.get("bkt_delta_per_skill", {}),
				"criticality_scores": e.get("criticality_scores", {}),
				"prerequisite_chain": e.get("prerequisite_chain", []),
				"z3_result": e.get("z3_result", {}),
				"rejection_reason": e.get("rejection_reason"),
			}
		)

	if db_conn is not None:
		try:
			cursor = db_conn.cursor()
			for row in normalized:
				cursor.execute(
					"INSERT INTO decision_ledger (session_id, entry) VALUES (%s, %s)",
					(session_id, row),
				)
			db_conn.commit()
		except Exception:
			# Trace persistence is non-blocking for path generation.
			pass

	return {"session_id": session_id, "entries": normalized}
