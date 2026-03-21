"""Plain-English path justification rendering from structured provenance."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from groq import Groq

SYSTEM_PROMPT = (
	"You receive structured decision data. Render ONE plain-English sentence per module "
	"explaining WHY it was included. Never invent facts. Use only the provided fields: "
	"skill_name, p_m_before, p_m_after, prerequisite_chain, criticality_score."
)


def _template_justifications(ledger: dict) -> List[str]:
	outputs: list[str] = []
	for entry in ledger.get("entries", []):
		module_id = entry.get("action_module_id", "module")
		deltas = entry.get("bkt_delta_per_skill", {})
		if deltas:
			skill_name, delta = next(iter(deltas.items()))
			outputs.append(
				f"{module_id} was selected to improve {skill_name} by {float(delta):.3f} while respecting prerequisites."
			)
		else:
			outputs.append(f"{module_id} was selected because it satisfies required prerequisite and compliance constraints.")
	return outputs


def render_justifications(ledger: dict) -> List[str]:
	"""Generate one human-readable justification sentence per module."""
	api_key = os.getenv("GROQ_API_KEY")
	timeout_s = float(os.getenv("GROQ_TIMEOUT_SECONDS", "2"))
	if not api_key:
		return _template_justifications(ledger)

	try:
		client = Groq(api_key=api_key, timeout=timeout_s)
		completion = client.chat.completions.create(
			model="qwen-2.5-7b",
			temperature=0,
			response_format={"type": "json_object"},
			messages=[
				{"role": "system", "content": SYSTEM_PROMPT},
				{
					"role": "user",
					"content": (
						"Return JSON object with a single field `justifications` as an array of strings.\n"
						f"Data:\n{json.dumps(ledger, ensure_ascii=True)}"
					),
				},
			],
		)
		raw = completion.choices[0].message.content or "{}"
		parsed = json.loads(raw)
		justifications = parsed.get("justifications", [])
		if isinstance(justifications, list) and all(isinstance(i, str) for i in justifications):
			return justifications
	except Exception:
		pass

	return _template_justifications(ledger)
