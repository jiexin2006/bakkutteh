from __future__ import annotations

import json

from Prompt import get_financial_reasoning_prompt
from ZAI import ZAI


class ResponseParseError(ValueError):
	"""Raised when model output cannot be parsed as JSON."""


def _strip_markdown_fence(text: str) -> str:
	cleaned = text.strip()
	if cleaned.startswith("```"):
		lines = cleaned.splitlines()
		if lines and lines[0].startswith("```"):
			lines = lines[1:]
		if lines and lines[-1].strip() == "```":
			lines = lines[:-1]
		cleaned = "\n".join(lines).strip()
	return cleaned


def _extract_json_block(text: str) -> str:
	"""Try to recover a JSON object payload from model output text."""
	cleaned = _strip_markdown_fence(text)

	# Fast path: full string is valid JSON
	try:
		json.loads(cleaned)
		return cleaned
	except json.JSONDecodeError:
		pass

	start = cleaned.find("{")
	end = cleaned.rfind("}")
	if start == -1 or end == -1 or end <= start:
		raise ResponseParseError("No JSON object found in model response.")

	candidate = cleaned[start : end + 1]
	try:
		json.loads(candidate)
		return candidate
	except json.JSONDecodeError as exc:
		raise ResponseParseError(f"Unable to parse model response JSON: {exc}") from exc


def parse_model_json(response_text: str) -> dict:
	"""Parse model output text into a JSON dictionary."""
	json_block = _extract_json_block(response_text)
	payload = json.loads(json_block)
	if not isinstance(payload, dict):
		raise ResponseParseError("Expected top-level JSON object from model response.")
	return payload


def get_zai_response_json(
	user_data: dict,
	decision_context: dict,
	epf_analysis: dict,
	market_data: dict,
) -> dict:
	"""Call ZAI with prompt+data and return parsed JSON output."""
	prompt = get_financial_reasoning_prompt(
		user_data=user_data,
		allocation=decision_context,
		epf_analysis=epf_analysis,
		fd_market_data=market_data,
	)

	zai = ZAI()
	response_text = zai.chat_with_ilmu(prompt)
	return parse_model_json(response_text)
