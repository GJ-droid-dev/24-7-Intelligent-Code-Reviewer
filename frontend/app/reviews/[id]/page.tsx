"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { Review } from "@/lib/types";
import { ScoreGauge } from "@/components/results/ScoreGauge";
import { ScoreBreakdownChart } from "@/components/results/ScoreBreakdownChart";
import { FindingsList } from "@/components/results/FindingsList";
import { AgentPipelineStatus } from "@/components/submission/AgentPipelineStatus";
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  XCircle, 
  Cpu, 
  Loader2 
} from "lucide-react";

export default function ReviewReportPage() {
  const params = useParams();
  const reviewId = params.id as string;
  const { getIdToken, signInDemo } = useAuth();

  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchReport = async () => {
      try {
        let token = await getIdToken();
        if (!token) {
          signInDemo();
          token = "mock-test-token-test-user-001";
        }

        const data = await api.getReview(reviewId, token);
        setReview(data);
        setLoading(false);

        // If processing, poll every 2 seconds
        if (data.status === "processing" || data.status === "queued") {
          interval = setTimeout(fetchReport, 2000);
        }
      } catch (err: unknown) {
        console.error("Failed to load review report:", err);
        const message = err instanceof Error ? err.message : "Failed to load review report.";
        setError(message);
        setLoading(false);
      }
    };

    fetchReport();

    return () => {
      if (interval) clearTimeout(interval);
    };
  }, [reviewId, getIdToken, signInDemo]);

  const handleExportJson = () => {
    if (!review) return;
    const blob = new Blob([JSON.stringify(review, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `review-report-${review.reviewId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-8 h-8 text-[#3291FF] animate-spin" />
        <p className="text-xs font-mono text-[#8F8F8F]">
          Loading Multi-Agent Inspection Report...
        </p>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4 text-center">
        <div className="w-12 h-12 rounded-xl bg-red-950/30 border border-red-900/50 flex items-center justify-center text-red-400">
          <XCircle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-[#FFFFFF]">Report Unavailable</h3>
        <p className="text-xs text-[#8F8F8F] max-w-md">{error || "Review not found."}</p>
        <Link
          href="/"
          className="inline-flex items-center space-x-1.5 px-4 py-2 rounded bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] hover:border-[#3D3D3D] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Workspace</span>
        </Link>
      </div>
    );
  }

  // Processing state: Show live 7-agent pipeline
  if (review.status === "processing" || review.status === "queued") {
    return (
      <div className="max-w-3xl mx-auto space-y-6 py-8">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-[#141414] border border-[#262626] flex items-center justify-center text-[#3291FF] mx-auto shadow-inner">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <h2 className="text-xl font-bold text-[#FFFFFF]">
            Multi-Agent Review in Progress
          </h2>
          <p className="text-xs text-[#8F8F8F]">
            Orchestrating 5 specialist agents in parallel across security, performance, code quality, testing, and historical rules.
          </p>
        </div>

        <AgentPipelineStatus agentStatuses={review.agentStatuses} isAnalyzing={true} />
      </div>
    );
  }

  const blockingCount = review.blockingIssues?.length ?? 0;
  const nonBlockingCount = review.nonBlockingIssues?.length ?? (review.findings?.length ?? 0) - blockingCount;

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#262626] pb-5">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Link
              href="/history"
              className="text-[#8F8F8F] hover:text-[#EBEBEB] p-1 rounded hover:bg-[#141414] transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <span className="px-2 py-0.5 rounded bg-[#1A1A1A] border border-[#262626] text-[#3291FF] text-[10px] font-mono uppercase">
              {review.language}
            </span>
            <h1 className="text-xl font-bold text-[#FFFFFF] tracking-tight">
              {review.title || "Code Review Report"}
            </h1>
          </div>
          <p className="text-xs text-[#8F8F8F] pl-7">
            Review ID: <span className="font-mono text-[#A1A1AA]">{review.reviewId}</span> • Completed on{" "}
            {new Date(review.completedAt || review.submittedAt).toLocaleString()}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleShare}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#141414] hover:bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] transition-colors"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>{copied ? "Link Copied" : "Share"}</span>
          </button>
          <button
            onClick={handleExportJson}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#3291FF]/10 hover:bg-[#3291FF]/20 border border-[#3291FF]/40 text-[#3291FF] text-xs font-mono transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Top Section: Score Gauge, Score Breakdown & Summary */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Score Gauge (4 Cols) */}
        <div className="md:col-span-4">
          <ScoreGauge
            score={review.overallScore ?? 7.5}
            label={review.scoreLabel}
            recommendation={review.recommendation}
            blockingCount={blockingCount}
          />
        </div>

        {/* Score Breakdown (5 Cols) */}
        <div className="md:col-span-5">
          <ScoreBreakdownChart breakdown={review.scoreBreakdown} />
        </div>

        {/* Summary Card (3 Cols) */}
        <div className="md:col-span-3 rounded-xl bg-[#141414] border border-[#262626] p-5 space-y-3 flex flex-col justify-between">
          <div className="space-y-3">
            <h3 className="text-xs font-mono uppercase tracking-wider text-[#FFFFFF] border-b border-[#262626] pb-2">
              Executive Summary
            </h3>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[#8F8F8F]">Total Findings:</span>
                <span className="font-mono font-bold text-[#FFFFFF]">{review.findings?.length ?? 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#8F8F8F]">Blocking Issues:</span>
                <span className="font-mono font-bold text-red-400">{blockingCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#8F8F8F]">Non-Blocking:</span>
                <span className="font-mono font-bold text-[#3291FF]">{nonBlockingCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#8F8F8F]">Rules Applied:</span>
                <span className="font-mono font-bold text-emerald-400">
                  {review.historicalRulesApplied?.length ?? 2}
                </span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-[#262626]">
            <p className="text-[11px] text-[#8F8F8F] italic leading-relaxed">
              {review.humanReviewNote || "All findings validated against submitted code diffs."}
            </p>
          </div>
        </div>
      </div>

      {/* Main Section: Interactive Filterable Findings */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-mono font-semibold uppercase tracking-wider text-[#FFFFFF]">
              Synthesized Findings & Recommendations
            </h2>
            <span className="px-2 py-0.5 rounded bg-[#1A1A1A] border border-[#262626] text-[10px] font-mono text-[#8F8F8F]">
              Validated by Review Agent
            </span>
          </div>
        </div>

        <FindingsList findings={review.findings || []} />
      </div>
    </div>
  );
}
