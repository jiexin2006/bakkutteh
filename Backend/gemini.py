import os
import requests
from dotenv import load_dotenv

# Ensure we load .env from the root directory and override any global env variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)
API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiError(Exception):
    """Raised when Gemini API request fails."""

class Gemini:
    def __init__(self):
        self.model = "gemini-flash-latest"

    def chat(self, user_message: str) -> str:
        """Call Gemini API and return the assistant's response text."""
        if not API_KEY:
            raise GeminiError("Missing GEMINI_API_KEY environment variable.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': API_KEY
        }
        payload = {
            "contents": [{
                "parts": [{"text": user_message}]
            }]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            try:
                # Gemini response structure: data['candidates'][0]['content']['parts'][0]['text']
                return data['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError) as exc:
                raise GeminiError(f"Unexpected Gemini response format: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            if exc.response is not None:
                print(f"[ERROR] Gemini API Error Response: {exc.response.text}")
            raise GeminiError(f"Gemini API request failed: {exc}") from exc

    def chat_with_ilmu(self, user_message: str) -> str:
        """Alias for chat() to maintain parity with ZAI interface."""
        return self.chat(user_message)
