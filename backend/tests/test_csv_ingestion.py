# ============================================================
# Tests — CSV Rules Ingestion Service
# ============================================================

import pytest
from app.services.csv_ingestion import parse_rules_csv


def test_parse_rules_csv_valid():
    csv_text = """id,type,description
1,formatting,Avoid single-character variable names
2,performance,Cache repeated database lookups
3,security,Never interpolate raw user input directly into SQL
"""
    rules = parse_rules_csv(csv_text)
    assert len(rules) == 3
    assert rules[0]["id"] == "1"
    assert rules[0]["type"] == "formatting"
    assert rules[0]["description"] == "Avoid single-character variable names"
    assert rules[2]["type"] == "security"


def test_parse_rules_csv_empty():
    assert parse_rules_csv("") == []
    assert parse_rules_csv("id,type,description\n") == []


def test_parse_rules_csv_missing_fields():
    csv_text = """id,type,description
1,,Valid description
,security,Missing id
3,performance,
"""
    rules = parse_rules_csv(csv_text)
    assert len(rules) == 1
    assert rules[0]["id"] == "1"
    assert rules[0]["type"] == "general"
