# ============================================================
# Tests — Language Detection Service
# ============================================================

import pytest
from app.services.language_detector import detect_language


def test_detect_python():
    code = """
def calculate_metrics(values: list[float]) -> dict:
    total = sum(values)
    return {"total": total, "count": len(values)}
"""
    assert detect_language(code) == "python"


def test_detect_javascript():
    code = """
const express = require('express');
const app = express();
app.get('/api/health', (req, res) => {
    console.log("Health check");
    res.json({ status: 'ok' });
});
"""
    assert detect_language(code) == "javascript"


def test_detect_typescript():
    code = """
interface UserProfile {
    id: string;
    email: string;
    isActive: boolean;
}

export function formatUser(user: UserProfile): string {
    return `${user.id}: ${user.email}`;
}
"""
    assert detect_language(code) == "typescript"


def test_detect_java():
    code = """
package com.example.service;

public class OrderService {
    public static void main(String[] args) {
        System.out.println("Processing order");
    }
}
"""
    assert detect_language(code) == "java"


def test_detect_go():
    code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
"""
    assert detect_language(code) == "go"


def test_detect_with_hint():
    code = "x = 10"
    assert detect_language(code, hint="python") == "python"
    assert detect_language(code, hint="typescript") == "typescript"


def test_detect_empty_code():
    assert detect_language("") == "text"
    assert detect_language("   ") == "text"
