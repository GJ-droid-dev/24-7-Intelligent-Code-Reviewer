"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { CodeEditor, SAMPLE_SNIPPETS } from "@/components/submission/CodeEditor";
import { AgentPipelineStatus } from "@/components/submission/AgentPipelineStatus";
import { FieldTooltip } from "@/components/submission/FieldTooltip";
import { 
  Play, 
  Loader2, 
  CheckCircle2, 
  AlertCircle 
} from "lucide-react";

export default function SubmitWorkspacePage() {
  const router = useRouter();
  const { getIdToken, signInDemo } = useAuth();

  const [title, setTitle] = useState("Add customer order-history API");
  const [description, setDescription] = useState("Expose GET /orders/history endpoint with customer filter and order item aggregation.");
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(SAMPLE_SNIPPETS.python_order_api.code);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!code.trim()) {
      setError("Please input or paste code snippet to review.");
      return;
    }

    try {
      setSubmitting(true);
      let token = await getIdToken();
      
      // Auto-activate demo user if user isn't logged in
      if (!token) {
        signInDemo();
        token = "mock-test-token-test-user-001";
      }

      const review = await api.submitReview(
        {
          title,
          description: description || undefined,
          language,
          code,
        },
        token
      );

      // Navigate directly to dedicated review report page
      router.push(`/reviews/${review.reviewId}`);
    } catch (err: unknown) {
      console.error("Submission failed:", err);
      const message = err instanceof Error ? err.message : "Failed to submit review. Ensure backend is running.";
      setError(message);
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#262626]">
        <div>
          <h1 className="text-xl font-bold text-[#FFFFFF] tracking-tight flex items-center space-x-2">
            <span>Precision Editorial Workspace</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#3291FF]/10 text-[#3291FF] border border-[#3291FF]/30">
              Active Session
            </span>
          </h1>
          <p className="text-xs text-[#8F8F8F] mt-1">
            Dispatch code diffs directly through the asynchronous 7-Agent AI review matrix.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={() => {
              setTitle("Add customer order-history API");
              setDescription("Expose GET /orders/history endpoint with customer filter and order item aggregation.");
              setLanguage("python");
              setCode(SAMPLE_SNIPPETS.python_order_api.code);
            }}
            className="px-3 py-1.5 rounded bg-[#141414] hover:bg-[#1F1F1F] border border-[#262626] text-xs text-[#8F8F8F] hover:text-[#EBEBEB] transition-all font-mono"
          >
            Reset Template
          </button>
        </div>
      </div>

      {/* Submission Error Banner */}
      {error && (
        <div className="p-3.5 rounded-lg bg-red-950/30 border border-red-900/50 flex items-start space-x-2 text-xs text-red-400 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold">Submission Error</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Main Split-Pane Layout */}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Pane: Code Editor & Metadata Inputs (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Metadata Inputs Card */}
          <div className="rounded-lg bg-[#141414] border border-[#262626] p-4 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[11px] font-mono text-[#8F8F8F] uppercase flex items-center">
                  <span>Pull Request / Change Title</span>
                  <FieldTooltip
                    title="Change Intent & Scope"
                    description="Defines the core business objective and expected functionality of the code modification."
                    agentImpact="Agents match your code against this intent to catch scope creep, verify completeness, and frame the executive summary."
                    align="left"
                  />
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Add order history endpoint"
                  className="w-full px-3 py-2 rounded bg-[#0A0A0A] border border-[#262626] text-xs text-[#EBEBEB] focus:outline-none focus:border-[#3291FF]"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-mono text-[#8F8F8F] uppercase flex items-center">
                  <span>Target Service / Component</span>
                  <FieldTooltip
                    title="Architectural Tier & Rules"
                    description="Identifies the file path, service tier, or layer being modified (e.g. API router, database repository, frontend component)."
                    agentImpact="Triggers layer-specific checks (e.g. HTTP status codes for routers, N+1 queries for DB) and fetches historical team rules."
                    align="right"
                  />
                </label>
                <input
                  type="text"
                  defaultValue="backend/app/routers/orders.py"
                  className="w-full px-3 py-2 rounded bg-[#0A0A0A] border border-[#262626] text-xs text-[#8F8F8F] focus:outline-none focus:border-[#3291FF]"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-mono text-[#8F8F8F] uppercase flex items-center">
                <span>Context / Architectural Notes (Optional)</span>
                <FieldTooltip
                  title="Design Constraints & Trade-offs"
                  description="Provides background constraints, traffic load assumptions, intentional trade-offs, or security policies not obvious from the diff alone."
                  agentImpact="Suppresses false-positive warnings for intentional design choices and grounds Architecture & Scalability analysis."
                  align="left"
                />
              </label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe expected load, auth policies, or database constraints..."
                className="w-full px-3 py-2 rounded bg-[#0A0A0A] border border-[#262626] text-xs text-[#EBEBEB] focus:outline-none focus:border-[#3291FF] resize-none"
              />
            </div>
          </div>

          {/* Monaco Code Editor */}
          <div className="h-[460px]">
            <CodeEditor
              value={code}
              onChange={setCode}
              language={language}
              onLanguageChange={setLanguage}
            />
          </div>
        </div>

        {/* Right Pane: 7-Agent Pipeline & Run Trigger (5 Cols) */}
        <div className="lg:col-span-5 space-y-4 flex flex-col justify-between">
          <AgentPipelineStatus isAnalyzing={submitting} />

          {/* Review Capabilities Card */}
          <div className="rounded-lg bg-[#141414] border border-[#262626] p-4 space-y-3">
            <h4 className="text-xs font-mono font-semibold text-[#FFFFFF] uppercase tracking-wider">
              Automated Inspection Scope
            </h4>
            <ul className="space-y-2 text-xs text-[#8F8F8F]">
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>OWASP Top 10, Auth/Authz gaps & IDOR detection</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>N+1 query detection, missing pagination & caching checks</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Missing negative test cases & boundary assertion analysis</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Firestore-backed historical repository rule matching</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Standardized 1–10 quality score with safety floor bounds</span>
              </li>
            </ul>
          </div>

          {/* Run Review CTA */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3.5 px-4 rounded-lg bg-[#3291FF] hover:bg-[#0070F3] disabled:opacity-50 text-[#FFFFFF] font-semibold text-xs font-mono uppercase tracking-wider shadow-[0_0_25px_rgba(50,145,255,0.3)] hover:shadow-[0_0_35px_rgba(50,145,255,0.5)] transition-all flex items-center justify-center space-x-2"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Orchestrating 7-Agent Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run 7-Agent Code Review</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
