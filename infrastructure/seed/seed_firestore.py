"""
Firestore Seed Script — Multi-Agent AI Code Reviewer

Seeds the Firestore database with:
  1. Historical review rules from CSV
  2. A sample test user
  3. A sample review with findings (for development/testing)

Usage:
  python seed_firestore.py --project <GCP_PROJECT_ID> [--csv <PATH_TO_CSV>]

Prerequisites:
  - pip install google-cloud-firestore
  - Authenticated via `gcloud auth application-default login`
    OR GOOGLE_APPLICATION_CREDENTIALS env var set to a service account key
"""

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from google.cloud import firestore
except ImportError:
    print("ERROR: google-cloud-firestore is not installed.")
    print("Run: pip install google-cloud-firestore")
    sys.exit(1)


# ─── Default Paths ───────────────────────────────────────────────────────────

DEFAULT_CSV_PATH = Path(__file__).parent / "historical_reviews.csv"


# ─── Seed Functions ──────────────────────────────────────────────────────────

def seed_rules(db: firestore.Client, csv_path: Path) -> int:
    """Parse historical_reviews.csv and upsert each rule into the 'rules' collection."""
    if not csv_path.exists():
        print(f"WARNING: CSV file not found at {csv_path}. Skipping rules seeding.")
        return 0

    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule_id = row["id"].strip()
            rule_type = row["type"].strip()
            description = row["description"].strip()

            db.collection("rules").document(rule_id).set({
                "id": rule_id,
                "type": rule_type,
                "description": description,
                "ingestedAt": firestore.SERVER_TIMESTAMP,
            })
            count += 1
            print(f"  ✓ Rule {rule_id} ({rule_type})")

    return count


def seed_sample_user(db: firestore.Client) -> str:
    """Create a sample test user document."""
    user_id = "test-user-001"
    db.collection("users").document(user_id).set({
        "uid": user_id,
        "email": "testuser@example.com",
        "displayName": "Test Developer",
        "createdAt": firestore.SERVER_TIMESTAMP,
    })
    print(f"  ✓ User: {user_id}")
    return user_id


def seed_sample_review(db: firestore.Client, user_id: str) -> str:
    """Create a sample review with findings for testing."""
    review_id = "sample-review-001"

    # Create review document
    db.collection("reviews").document(review_id).set({
        "userId": user_id,
        "language": "python",
        "codeSnippet": (
            "def get_orders(customer_id):\n"
            "    query = f\"SELECT * FROM orders WHERE customer_id = {customer_id}\"\n"
            "    results = db.execute(query)\n"
            "    return results\n"
        ),
        "overallScore": 4,
        "scoreBreakdown": {
            "security": 2,
            "performance": 4,
            "codeQuality": 5,
            "testCoverage": 4,
            "historical": 5,
        },
        "submittedAt": firestore.SERVER_TIMESTAMP,
        "status": "complete",
    })
    print(f"  ✓ Review: {review_id}")

    # Create findings sub-collection
    findings = [
        {
            "agentSource": "security",
            "category": "Blocking Issue",
            "severity": "critical",
            "description": (
                "The API endpoint accepts a customer ID but does not verify that "
                "the authenticated user owns that customer record."
            ),
            "suggestedFix": "Add ownership validation before returning data.",
            "matchedRuleId": "11",
        },
        {
            "agentSource": "security",
            "category": "SQL Injection",
            "severity": "critical",
            "description": (
                "Raw user input is interpolated directly into a SQL query string. "
                "This is vulnerable to SQL injection attacks."
            ),
            "suggestedFix": "Use parameterized queries instead of f-string interpolation.",
            "matchedRuleId": "10",
        },
        {
            "agentSource": "performance",
            "category": "Performance",
            "severity": "high",
            "description": (
                "The endpoint returns all order history without pagination, "
                "which may create slow responses for large accounts."
            ),
            "suggestedFix": "Add pagination with LIMIT and OFFSET, or cursor-based pagination.",
            "matchedRuleId": "6",
        },
        {
            "agentSource": "test-edge-case",
            "category": "Testing",
            "severity": "medium",
            "description": (
                "No tests present for unauthorized access, invalid customer IDs, "
                "empty order history, or pagination behavior."
            ),
            "suggestedFix": "Add unit tests covering error paths and edge cases.",
            "matchedRuleId": None,
        },
        {
            "agentSource": "code-quality",
            "category": "Code Quality",
            "severity": "low",
            "description": (
                "The function mixes request handling, database logic, and response "
                "formatting in a single function."
            ),
            "suggestedFix": "Separate into service/repository layers.",
            "matchedRuleId": "21",
        },
    ]

    for i, finding in enumerate(findings):
        finding_id = f"finding-{i + 1:03d}"
        db.collection("reviews").document(review_id).collection("findings").document(finding_id).set(finding)
        print(f"    ✓ Finding: {finding_id} ({finding['severity']})")

    return review_id


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed Firestore with initial data")
    parser.add_argument(
        "--project",
        required=True,
        help="GCP Project ID",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help=f"Path to historical_reviews.csv (default: {DEFAULT_CSV_PATH})",
    )
    args = parser.parse_args()

    print(f"\n🌱 Seeding Firestore for project: {args.project}\n")

    db = firestore.Client(project=args.project)

    # 1. Seed historical rules from CSV
    print("📋 Seeding historical rules...")
    rule_count = seed_rules(db, args.csv)
    print(f"   → {rule_count} rules seeded\n")

    # 2. Seed sample user
    print("👤 Seeding sample user...")
    user_id = seed_sample_user(db)
    print()

    # 3. Seed sample review with findings
    print("📝 Seeding sample review...")
    review_id = seed_sample_review(db, user_id)
    print()

    print(f"✅ Seeding complete!")
    print(f"   • {rule_count} rules")
    print(f"   • 1 user ({user_id})")
    print(f"   • 1 review ({review_id}) with 5 findings")
    print()


if __name__ == "__main__":
    main()
