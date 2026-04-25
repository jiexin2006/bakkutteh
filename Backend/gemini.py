import os
import logging
from secrets_manager import get_secret

# Configuration from Secret Manager / Env
PROJECT_ID = get_secret("GCP_PROJECT_ID")
LOCATION = get_secret("GCP_LOCATION", "us-central1")

logger = logging.getLogger("bakkutteh.gemini")

class GeminiError(Exception):
    """Raised when Gemini API request fails."""

class Gemini:
    def __init__(self):
        self.model_name = "gemini-1.5-flash"
        self.client = None
        
        try:
            # Import inside __init__ to avoid startup crashes if libraries are missing
            from google import genai
            
            if PROJECT_ID:
                # Initialize for Vertex AI (Google Cloud)
                self.client = genai.Client(
                    vertexai=True,
                    project=PROJECT_ID,
                    location=LOCATION
                )
                logger.info(f"Initialized Gemini via Google Gen AI SDK (Vertex AI Mode: {PROJECT_ID})")
            else:
                # Fallback to AI Studio if no Project ID (using API Key from Secret Manager)
                api_key = get_secret("GEMINI_API_KEY")
                if api_key:
                    self.client = genai.Client(api_key=api_key)
                    logger.info("Initialized Gemini via Google Gen AI SDK (AI Studio Mode)")
        except ImportError:
            logger.warning("google-genai library not found. Gemini fallback will be unavailable.")
        except Exception as exc:
            logger.error(f"Failed to initialize Google Gen AI client: {exc}")

    def chat(self, user_message: str) -> str:
        """Call Gemini via the unified Gen AI SDK and return response text."""
        if not self.client:
            raise GeminiError("Gemini client not initialized. Check GCP_PROJECT_ID or GEMINI_API_KEY.")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message
            )
            return response.text
        except Exception as exc:
            raise GeminiError(f"Google Gen AI request failed: {exc}") from exc

    def chat_with_ilmu(self, user_message: str) -> str:
        """Maintain parity with ZAI interface."""
        return self.chat(user_message)
