# ============================================================
# CSV Ingestion Service — Rules Ingestion on Startup
# ============================================================

import csv
import io
import logging
import os
from typing import List, Dict, Any, Optional
from google.cloud import storage
from google.cloud import firestore
from app.config import settings
from app.dependencies import get_firestore_client

logger = logging.getLogger(__name__)


def fetch_csv_content() -> Optional[str]:
    """
    Fetch CSV rules from Cloud Storage or fallback to local seed CSV.
    """
    # 1. Try Google Cloud Storage
    try:
        storage_client = storage.Client(project=settings.gcp_project_id)
        bucket = storage_client.bucket(settings.gcs_rules_bucket)
        blob = bucket.blob(settings.gcs_rules_csv_path)

        if blob.exists():
            content = blob.download_as_text(encoding="utf-8")
            logger.info(f"Successfully downloaded CSV rules from gs://{settings.gcs_rules_bucket}/{settings.gcs_rules_csv_path}")
            return content
        else:
            logger.warning(f"GCS blob not found at gs://{settings.gcs_rules_bucket}/{settings.gcs_rules_csv_path}")
    except Exception as e:
        logger.warning(f"Could not fetch rules from GCS ({e}). Attempting local fallback.")

    # 2. Fallback to local repository seed file
    local_candidates = [
        os.path.join(os.getcwd(), "infrastructure", "seed", "historical_reviews.csv"),
        os.path.join(os.getcwd(), "..", "infrastructure", "seed", "historical_reviews.csv"),
        "historical_reviews.csv",
    ]

    for candidate in local_candidates:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    content = f.read()
                    logger.info(f"Loaded rules from local file: {candidate}")
                    return content
            except Exception as e:
                logger.error(f"Failed to read local fallback CSV {candidate}: {e}")

    logger.error("No rules CSV could be located from GCS or local filesystem.")
    return None


def parse_rules_csv(csv_text: str) -> List[Dict[str, Any]]:
    """
    Parse CSV text into list of rule dicts: [{'id': '1', 'type': 'formatting', 'description': '...'}]
    """
    rules = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        rule_id = row.get("id", "").strip()
        rule_type = row.get("type", "").strip()
        description = row.get("description", "").strip()

        if rule_id and description:
            rules.append({
                "id": rule_id,
                "type": rule_type or "general",
                "description": description,
            })
    return rules


def ingest_rules_into_firestore(db: Optional[firestore.Client] = None) -> int:
    """
    Orchestrates downloading CSV, parsing rules, and upserting into Firestore 'rules' collection.
    Returns the count of ingested rules.
    """
    csv_content = fetch_csv_content()
    if not csv_content:
        logger.warning("Skipping rule ingestion — no CSV content available.")
        return 0

    rules = parse_rules_csv(csv_content)
    if not rules:
        logger.warning("No valid rules found in CSV.")
        return 0

    if db is None:
        try:
            db = get_firestore_client()
        except Exception as e:
            logger.error(f"Cannot ingest rules — Firestore client unavailable: {e}")
            return 0

    batch = db.batch()
    batch_count = 0
    total_ingested = 0

    for rule in rules:
        doc_ref = db.collection("rules").document(rule["id"])
        batch.set(doc_ref, {
            "type": rule["type"],
            "description": rule["description"],
            "updatedAt": firestore.SERVER_TIMESTAMP,
        }, merge=True)
        batch_count += 1
        total_ingested += 1

        if batch_count >= 450:
            batch.commit()
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()

    logger.info(f"Ingested {total_ingested} rules into Firestore 'rules' collection.")
    return total_ingested
