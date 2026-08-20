import sys
import os
import json
import asyncio

# Ensure backend directory is in the sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from tests.synthetic_code_sets import SYNTHETIC_TEST_SUITE

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer mock-test-token"}

def run_tests():
    print("============================================================")
    print(" Running Synthetic Code Sets through Multi-Agent AI Reviewer")
    print("============================================================\n")

    for level, code in SYNTHETIC_TEST_SUITE.items():
        print(f"--- Submitting '{level.upper()}' Code Set ---")
        
        # 1. Submit Review
        submit_res = client.post(
            "/api/v1/reviews", 
            json={"code": code, "title": f"Synthetic {level.title()} Test"}, 
            headers=AUTH_HEADER
        )
        
        if submit_res.status_code != 202:
            print(f"[ERROR] Failed to submit {level} test. Status {submit_res.status_code}: {submit_res.text}\n")
            continue
            
        review_id = submit_res.json().get("reviewId")
        print(f"[*] Submitted successfully. Review ID: {review_id}")
        
        # 2. Retrieve Review Results
        get_res = client.get(f"/api/v1/reviews/{review_id}", headers=AUTH_HEADER)
        
        if get_res.status_code != 200:
            print(f"[ERROR] Failed to fetch results for {review_id}. Status {get_res.status_code}: {get_res.text}\n")
            continue
            
        report = get_res.json()
        
        # 3. Print Summary
        status = report.get("status")
        if status == "error":
            print(f"[!] Pipeline Error: {report.get('errorMessage')}\n")
            continue
            
        score = report.get("overallScore")
        breakdown = report.get("scoreBreakdown", {})
        findings = report.get("findings", [])
        
        print(f"[*] Status: {status}")
        print(f"[*] Overall Score: {score}/10")
        print(f"[*] Score Breakdown: {breakdown}")
        print(f"[*] Findings Count: {len(findings)}")
        
        print("[*] Findings:")
        for idx, finding in enumerate(findings[:6]):
            agent = finding.get("agentSource", "unknown")
            severity = finding.get("severity", "unknown").upper()
            category = finding.get("category", "unknown").upper()
            title = finding.get("title", "No Title")
            desc = finding.get("description", "")
            if len(desc) > 90:
                desc = desc[:87] + "..."
            print(f"    {idx+1}. [{severity}] [{agent}] {title}")
            print(f"       Description: {desc}")
            
        if len(findings) > 6:
            print(f"    ... and {len(findings) - 6} more findings.")
            
        print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    run_tests()
