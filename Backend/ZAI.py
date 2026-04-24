from __future__ import annotations

import os
from typing import Any
from dotenv import load_dotenv

try:
	from zai import ZaiClient
except ImportError as exc:  
	ZaiClient = None
	_ZAI_IMPORT_ERROR = exc


MODEL = "ilmu-glm-5.1"

load_dotenv()
API_KEY = os.getenv("ILMU_API_KEY")

class IlmuApiError(Exception):
	"""Raised when ILMU API request fails."""

class ZAI:
	def __init__(self):
		self.client = self._build_client()

	def _build_client(self):
		"""Create a ZAI client using the configured API key."""
		if not API_KEY:
			raise IlmuApiError(
				"Missing API key. Please set the ILMU_API_KEY environment variable."
			)

		if ZaiClient is None:
			raise IlmuApiError(
				f"The 'zai' package is not installed: {_ZAI_IMPORT_ERROR}"
			)

		return ZaiClient(
			api_key=API_KEY,
			base_url="https://api.ilmu.ai/v1"
		)

	def _extract_content(self, response: Any) -> str:
		"""Extract the assistant's message content from the API response."""
		try:
			return response.choices[0].message.content
		except (AttributeError, IndexError) as exc:
			raise IlmuApiError(f"Unexpected API response format: {exc}") from exc

	def chat_with_ilmu(self, user_message: str, model: str = MODEL) -> str:
		"""Convenience helper that returns assistant text only."""
		response = self.client.chat.completions.create(
			model=model,
			messages=[
				{
					"role": "user",
					"content": user_message,
				},
			],
			thinking={
				"type": "enabled",
			},
			stream=False,
			max_tokens=4096,
			temperature=0.6,
		)
		return self._extract_content(response)
	
	def chat(self, message):
		return self.chat_with_ilmu(message)



# if __name__ == "__main__":
# 	zai = ZAI()
# 	print(zai.chat("Hello!"))
