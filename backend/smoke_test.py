# ============================================================
# Phase 2 Smoke Test & Validation Script
# ============================================================

import sys
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer mock-test-token"}


def run_validation():
    print("=" * 60)
    print("  PHASE 2 VALIDATION & SMOKE TEST SUITE")
    print("=" * 60)
    passed_checks = 0
    total_checks = 0

    def check(name: str, condition: bool, details: str = ""):
        nonlocal passed_checks, total_checks
        total_checks += 1
        if condition:
            passed_checks += 1
            print(f"  [PASS] {name} {details}")
        else:
            print(f"  [FAIL] {name} {details}")

    # 1. Root metadata check
    print("\n--- 1. Root & Health Checks ---")
    res = client.get("/")
    check("GET /", res.status_code == 200 and res.json().get("status") == "operational")

    res = client.get("/api/v1/health")
    health_data = res.json()
    check("GET /api/v1/health", res.status_code == 200 and health_data.get("status") == "healthy", f"({health_data.get('firestore')})")

    # 2. Authentication Enforcement
    print("\n--- 2. Auth Middleware Verification ---")
    res = client.get("/api/v1/reviews")
    check("Unauthenticated rejection (401)", res.status_code == 401)

    res = client.get("/api/v1/reviews", headers={"Authorization": "Bearer invalid_token"})
    check("Invalid token rejection (401)", res.status_code == 401)

    res = client.get("/api/v1/reviews", headers=AUTH_HEADER)
    check("Authenticated access (200)", res.status_code == 200)

    # 3. Multi-Language Code Submission & Detection
    print("\n--- 3. Multi-Language Review Submission ---")
    
    # Python
    py_code = """
def authenticate_user(username, password):
    query = f"SELECT * FROM users WHERE user = '{username}' AND pass = '{password}'"
    return db.execute(query)
"""
    res = client.post("/api/v1/reviews", json={"code": py_code, "title": "Auth Login"}, headers=AUTH_HEADER)
    check("Submit Python review (202)", res.status_code == 202)
    py_review_id = res.json().get("reviewId")
    check("Language auto-detection: python", res.json().get("language") == "python")

    # TypeScript
    ts_code = """
interface ReviewPayload {
    id: string;
    score: number;
}
export function formatPayload(p: ReviewPayload): string {
    return `Review #${p.id} with score ${p.score}`;
}
"""
    res = client.post("/api/v1/reviews", json={"code": ts_code, "title": "TS Formatter"}, headers=AUTH_HEADER)
    check("Submit TypeScript review (202)", res.status_code == 202)
    check("Language auto-detection: typescript", res.json().get("language") == "typescript")

    # Go
    go_code = """
package main
import "fmt"
func ProcessItems(items []string) {
    for _, item := range items {
        fmt.Println(item)
    }
}
"""
    res = client.post("/api/v1/reviews", json={"code": go_code, "title": "Go Loop"}, headers=AUTH_HEADER)
    check("Submit Go review (202)", res.status_code == 202)
    check("Language auto-detection: go", res.json().get("language") == "go")

    # 4. Review Report Retrieval & Findings
    print("\n--- 4. Review Report Retrieval & Findings ---")
    res = client.get(f"/api/v1/reviews/{py_review_id}", headers=AUTH_HEADER)
    check("GET /api/v1/reviews/{id} (200)", res.status_code == 200)
    report = res.json()
    check("Review status complete", report.get("status") == "complete")
    check("Overall score generated (1-10)", 1 <= report.get("overallScore", 0) <= 10, f"Score: {report.get('overallScore')}/10")
    check("Score breakdown present", "scoreBreakdown" in report and "security" in report["scoreBreakdown"])
    check("Findings categorized and sorted", len(report.get("findings", [])) > 0, f"({len(report.get('findings', []))} findings)")

    # 5. History & Pagination
    print("\n--- 5. Review History & Pagination ---")
    res = client.get("/api/v1/reviews?page=1&pageSize=5", headers=AUTH_HEADER)
    check("GET /api/v1/reviews paginated (200)", res.status_code == 200)
    list_data = res.json()
    check("Reviews list returned", len(list_data.get("reviews", [])) > 0, f"({len(list_data.get('reviews', []))} items on page 1)")
    check("Pagination metadata present", "total" in list_data and "hasMore" in list_data)

    print("\n" + "=" * 60)
    print(f"  VALIDATION SUMMARY: {passed_checks}/{total_checks} CHECKS PASSED")
    print("=" * 60)

    if passed_checks == total_checks:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    run_validation()
