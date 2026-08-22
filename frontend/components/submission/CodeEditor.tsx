"use client";

import React, { useState, useRef, useEffect } from "react";
import Editor from "@monaco-editor/react";
import { Code, Sparkles, Trash2, Copy, Check, ChevronDown } from "lucide-react";

interface CodeEditorProps {
  value: string;
  onChange: (val: string) => void;
  language: string;
  onLanguageChange: (lang: string) => void;
  onSelectSample?: (sample: { title: string; lang: string; code: string; desc: string }) => void;
  readOnly?: boolean;
}

export const SAMPLE_SNIPPETS: Record<string, { title: string; lang: string; code: string; desc: string }> = {
  python_order_api: {
    title: "Customer Order-History API (Python / FastAPI)",
    lang: "python",
    desc: "FastAPI endpoint with cross-user IDOR, unpaginated SQL query, and missing authorization tests.",
    code: `from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import sqlite3

router = APIRouter(prefix="/orders", tags=["orders"])

# Database connection helper
def get_db():
    conn = sqlite3.connect("production.db")
    return conn

@router.get("/history")
async def get_order_history(
    customer_id: str = Query(..., description="Target Customer ID"),
    status: Optional[str] = None
):
    # ISSUE 1: Missing ownership check (IDOR: user can request any customer_id)
    # ISSUE 2: Unbounded query without pagination / limit
    # ISSUE 3: SQL string interpolation vulnerability
    conn = get_db()
    cursor = conn.cursor()
    
    query = f"SELECT id, total, created_at, status FROM orders WHERE customer_id = '{customer_id}'"
    if status:
        query += f" AND status = '{status}'"
        
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # ISSUE 4: N+1 query loop over customer records
    results = []
    for row in rows:
        order_id = row[0]
        cursor.execute(f"SELECT item_name, price FROM order_items WHERE order_id = '{order_id}'")
        items = cursor.fetchall()
        results.append({
            "order_id": order_id,
            "total": row[1],
            "created_at": row[2],
            "status": row[3],
            "items": [{"name": i[0], "price": i[1]} for i in items]
        })
        
    return {"customer_id": customer_id, "orders": results}
`,
  },
  typescript_auth_service: {
    title: "JWT Auth Middleware (TypeScript)",
    lang: "typescript",
    desc: "Express/Next.js auth middleware with unverified signature algorithm fallback and secret leak.",
    code: `import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || "fallback-insecure-secret-key-12345";

export interface AuthenticatedRequest extends Request {
  user?: { id: string; role: string };
}

export function authMiddleware(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Missing authorization token" });
  }

  const token = authHeader.split(" ")[1];

  try {
    // SECURITY RISK: 'none' algorithm allowed or unverified issuer
    const decoded = jwt.verify(token, JWT_SECRET, { algorithms: ["HS256", "none" as unknown as jwt.Algorithm] }) as { sub: string; role: string };
    req.user = { id: decoded.sub, role: decoded.role };
    next();
  } catch (err: unknown) {
    // SENSITIVE LEAK: Printing raw error stack with token details
    const message = err instanceof Error ? err.message : "Authentication error";
    console.error("Auth failure for token:", token, message);
    return res.status(403).json({ error: "Invalid token", details: message });
  }
}
`,
  },
  go_worker_pool: {
    title: "Concurrent Task Worker Pool (Go)",
    lang: "go",
    desc: "Go async task scheduler with unbounded goroutines and missing context cancellation.",
    code: `package main

import (
	"context"
	"fmt"
	"net/http"
	"sync"
)

type Job struct {
	ID  string
	URL string
}

// ProcessJobs spawns unbounded goroutines without rate limiting or context timeouts
func ProcessJobs(ctx context.Context, jobs []Job) []string {
	var wg sync.WaitGroup
	results := make([]string, len(jobs))

	for i, job := range jobs {
		wg.Add(1)
		// CONCURRENCY RISK: Spawning unbounded goroutines per job item
		go func(index int, j Job) {
			defer wg.Done()
			
			// Lacks timeout or cancellation check
			resp, err := http.Get(j.URL)
			if err != nil {
				results[index] = fmt.Sprintf("Error: %v", err)
				return
			}
			defer resp.Body.Close()
			results[index] = fmt.Sprintf("Status: %d", resp.StatusCode)
		}(i, job)
	}

	wg.Wait()
	return results
}
`,
  },
};

export function CodeEditor({
  value,
  onChange,
  language,
  onLanguageChange,
  onSelectSample,
  readOnly = false,
}: CodeEditorProps) {
  const [copied, setCopied] = useState(false);
  const [isSampleOpen, setIsSampleOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsSampleOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsSampleOpen(false);
      }
    };

    if (isSampleOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isSampleOpen]);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSampleClick = (sample: { title: string; lang: string; code: string; desc: string }) => {
    if (onSelectSample) {
      onSelectSample(sample);
    } else {
      onChange(sample.code);
      onLanguageChange(sample.lang);
    }
    setIsSampleOpen(false);
  };

  const lineCount = value.split("\n").length;
  const charCount = value.length;

  return (
    <div className="flex flex-col h-full rounded-lg bg-[#141414] border border-[#262626] overflow-hidden">
      {/* Editor Header Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#101010] border-b border-[#262626]">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 text-xs font-mono text-[#EBEBEB]">
            <Code className="w-4 h-4 text-[#3291FF]" />
            <span>Code Input</span>
          </div>

          {/* Language Selector */}
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            disabled={readOnly}
            className="px-2.5 py-1 rounded bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF]"
          >
            <option value="auto">Auto Detect</option>
            <option value="python">Python</option>
            <option value="typescript">TypeScript</option>
            <option value="javascript">JavaScript</option>
            <option value="go">Go</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="rust">Rust</option>
            <option value="sql">SQL</option>
          </select>
        </div>

        {/* Action Controls & Sample Dropdown */}
        <div className="flex items-center space-x-2">
          {!readOnly && (
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setIsSampleOpen((prev) => !prev)}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded border text-xs font-mono transition-all ${
                  isSampleOpen
                    ? "bg-[#3291FF]/10 border-[#3291FF] text-[#3291FF]"
                    : "bg-[#1A1A1A] hover:bg-[#222222] border-[#3291FF]/40 text-[#3291FF]"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Load Sample</span>
                <ChevronDown className={`w-3 h-3 transition-transform duration-150 ${isSampleOpen ? "rotate-180" : ""}`} />
              </button>
              
              {isSampleOpen && (
                <div className="absolute right-0 mt-1.5 w-72 rounded-lg bg-[#141414] border border-[#333333] shadow-2xl p-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
                  <div className="flex items-center justify-between px-2 py-1 border-b border-[#262626] mb-1">
                    <p className="text-[10px] text-[#8F8F8F] font-mono uppercase tracking-wider font-semibold">
                      Select Test Scenario
                    </p>
                    <span className="text-[10px] font-mono text-[#3291FF] bg-[#3291FF]/10 px-1.5 py-0.5 rounded">
                      {Object.keys(SAMPLE_SNIPPETS).length} Samples
                    </span>
                  </div>
                  <div className="space-y-1">
                    {Object.entries(SAMPLE_SNIPPETS).map(([key, sample]) => (
                      <button
                        type="button"
                        key={key}
                        onClick={() => handleSampleClick(sample)}
                        className="w-full text-left p-2.5 rounded-md hover:bg-[#1F1F1F] active:bg-[#262626] text-xs text-[#EBEBEB] transition-colors group cursor-pointer border border-transparent hover:border-[#2D2D2D]"
                      >
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-[#EBEBEB] group-hover:text-[#3291FF] transition-colors">
                            {sample.title}
                          </p>
                          <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-[#1A1A1A] text-[#8F8F8F] border border-[#2A2A2A]">
                            {sample.lang}
                          </span>
                        </div>
                        <p className="text-[10px] text-[#8F8F8F] mt-0.5 leading-tight">
                          {sample.desc}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <button
            type="button"
            onClick={handleCopy}
            title="Copy Code"
            className="p-1.5 rounded hover:bg-[#1A1A1A] text-[#8F8F8F] hover:text-[#EBEBEB] transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          {!readOnly && (
            <button
              type="button"
              onClick={() => onChange("")}
              title="Clear Editor"
              className="p-1.5 rounded hover:bg-[#1A1A1A] text-[#8F8F8F] hover:text-red-400 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Monaco Editor Container */}
      <div className="flex-1 min-h-[420px] bg-[#0A0A0A]">
        <Editor
          height="100%"
          language={language === "auto" ? "python" : language}
          value={value}
          onChange={(val) => onChange(val || "")}
          theme="vs-dark"
          options={{
            readOnly,
            fontSize: 13,
            fontFamily: "'JetBrains Mono', monospace",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            lineNumbers: "on",
            glyphMargin: false,
            folding: true,
            lineDecorationsWidth: 8,
            lineNumbersMinChars: 3,
            renderLineHighlight: "all",
            overviewRulerBorder: false,
            cursorBlinking: "smooth",
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>

      {/* Editor Status Footer */}
      <div className="flex items-center justify-between px-4 py-1.5 bg-[#101010] border-t border-[#262626] text-[11px] font-mono text-[#8F8F8F]">
        <div className="flex items-center space-x-3">
          <span>{lineCount} lines</span>
          <span>•</span>
          <span>{charCount} characters</span>
        </div>
        <div className="flex items-center space-x-2">
          <span>UTF-8</span>
          <span>•</span>
          <span className="text-[#3291FF]">{language.toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
}
