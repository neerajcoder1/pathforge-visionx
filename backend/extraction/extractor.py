"""Skill mention extraction using Groq with local Ollama fallback."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, List

from groq import Groq

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
	"Extract skills as a JSON array with objects containing exactly: "
	"mention, context_20_tokens, source_section, proficiency_signal, implied_years."
)

@dataclass
class SkillMention:
	mention: str
	context_20_tokens: str
	source_section: str
	proficiency_signal: str
	implied_years: float


def _parse_mentions(payload: Any) -> List[SkillMention]:
	items = payload if isinstance(payload, list) else []
	mentions: list[SkillMention] = []
	for item in items:
		if not isinstance(item, dict):
			continue
		mention = str(item.get("mention", "")).strip()
		if not mention:
			continue
		mentions.append(
			SkillMention(
				mention=mention,
				context_20_tokens=str(item.get("context_20_tokens", "")).strip(),
				source_section=str(item.get("source_section", "resume")).strip() or "resume",
				proficiency_signal=str(item.get("proficiency_signal", "")).strip().lower(),
				implied_years=float(item.get("implied_years", 0.0) or 0.0),
			)
		)
	return mentions


def _extract_with_ollama(text: str) -> List[SkillMention]:
	"""Optional local fallback extractor; returns [] on failure."""
	try:
		import ollama
	except Exception as e:
		logger.error(f"LLM Extraction failed: {e}")
		return []

	user_prompt = (
		"Resume text:\n"
		f"{text[:12000]}\n\n"
		"Return JSON only, as an array of skill objects."
	)
	try:
		response = ollama.chat(
			model="llama3:8b",
			messages=[
				{"role": "system", "content": SYSTEM_PROMPT},
				{"role": "user", "content": user_prompt},
			],
			options={"temperature": 0},
		)
		content = response.get("message", {}).get("content", "[]")
		payload = json.loads(content)
		mentions = _parse_mentions(payload)
		if not mentions:
			logger.error("LLM Extraction failed: Ollama returned empty skill payload")
			return []
		return mentions
	except Exception as e:
		logger.error(f"LLM Extraction failed: {e}")
		return []


def extract_skills(text: str) -> List[SkillMention]:
	"""Extract skill mentions from text via Groq with a strict 2s timeout fallback."""
	timeout_s = float(os.getenv("GROQ_TIMEOUT_SECONDS", "2"))
	api_key = os.getenv("GROQ_API_KEY")
	user_prompt = (
		"Resume text:\n"
		f"{text[:12000]}\n\n"
		"Output JSON array only."
	)

	if not api_key:
		return _extract_with_ollama(text)

	try:
		client = Groq(api_key=api_key, timeout=timeout_s)
		print(f"Executing REAL Groq AI extraction...", flush=True)
		completion = client.chat.completions.create(
			model="phi-4-mini",
			temperature=0,
			response_format={"type": "json_object"},
			messages=[
				{"role": "system", "content": SYSTEM_PROMPT},
				{"role": "user", "content": user_prompt},
			],
		)
		raw = completion.choices[0].message.content or "{}"
		parsed = json.loads(raw)
		payload = parsed.get("skills", parsed)
		mentions = _parse_mentions(payload)
		if not mentions:
			logger.error("LLM Extraction failed: Groq returned empty skill payload")
			return []
		return mentions
	except Exception as e:
		logger.error(f"LLM Extraction failed: {e}")
		return []
