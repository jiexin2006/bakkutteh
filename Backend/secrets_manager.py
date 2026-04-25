import os
import logging
from dotenv import load_dotenv

# Fallback to .env for local development
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger("bakkutteh.secrets")

def get_secret(secret_id: str, default: str = None) -> str:
    """
    Fetch a secret from Google Cloud Secret Manager.
    Falls back to environment variables if GCP is unavailable.
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    
    # If no project ID is configured, we can't use Secret Manager
    # Return local env var immediately to avoid importing GCP libraries
    if not project_id:
        return os.getenv(secret_id, default)

    try:
        # Import inside the function to avoid startup crashes if libraries are missing
        from google.cloud import secretmanager
        
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except (ImportError, Exception) as exc:
        # Silently fallback to env vars if Secret Manager is not reachable/authenticated
        if not isinstance(exc, ImportError):
            logger.debug(f"Secret Manager failed for {secret_id}, using env fallback: {exc}")
        return os.getenv(secret_id, default)
