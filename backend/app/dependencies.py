# ============================================================
# Shared Dependencies — Database & External Services
# ============================================================

import os
import glob
import logging
from typing import Optional
from google.cloud import firestore
from google.oauth2 import service_account
from app.config import settings

logger = logging.getLogger(__name__)

# Singleton Firestore client
_firestore_client: Optional[firestore.Client] = None


def find_local_credentials_file() -> Optional[str]:
    """Search common paths for a local service account JSON key file."""
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and os.path.exists(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]):
        return os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    search_dirs = [
        os.getcwd(),
        os.path.abspath(os.path.join(os.getcwd(), "..")),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ]

    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
        # Check for firebase-adminsdk json files
        matches = glob.glob(os.path.join(directory, "*firebase-adminsdk*.json"))
        if matches:
            return matches[0]

    return None


def get_firestore_client() -> firestore.Client:
    """
    Dependency provider for Google Cloud Firestore client.
    Reuses existing client or initializes a new one.
    """
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client

    # Check for local service account key file
    cred_file = find_local_credentials_file()
    if cred_file and os.path.exists(cred_file):
        try:
            creds = service_account.Credentials.from_service_account_file(cred_file)
            _firestore_client = firestore.Client(project=settings.gcp_project_id, credentials=creds)
            logger.info(f"Connected to Firestore using credentials file: {cred_file}")
            return _firestore_client
        except Exception as e:
            logger.warning(f"Failed to initialize Firestore with key file {cred_file}: {e}")

    try:
        _firestore_client = firestore.Client(project=settings.gcp_project_id)
        logger.info(f"Connected to Firestore (project: {settings.gcp_project_id})")
        return _firestore_client
    except Exception as e:
        logger.error(f"Failed to initialize Firestore client: {e}")
        raise RuntimeError(f"Firestore client could not be initialized: {e}")


def set_firestore_client(client: Optional[firestore.Client]) -> None:
    """Setter used primarily for injecting mock Firestore client during testing."""
    global _firestore_client
    _firestore_client = client
