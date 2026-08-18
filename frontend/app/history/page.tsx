"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { Review } from "@/lib/types";
import { QualityTrendChart } from "@/components/history/QualityTrendChart";
import { HistoryTable } from "@/components/history/HistoryTable";
import { Plus, Loader2, RefreshCw } from "lucide-react";

export default function HistoryPage() {
  const { getIdToken, signInDemo } = useAuth();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      setRefreshing(true);
      let token = await getIdToken();
      if (!token) {
        signInDemo();
        token = "mock-test-token-test-user-001";
      }

      const data = await api.getReviews(token, 1, 50);
      setReviews(data.reviews || []);
    } catch (err) {
      console.error("Failed to load review history:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [getIdToken, signInDemo]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#262626] pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded bg-[#3291FF]/10 text-[#3291FF] text-[10px] font-mono uppercase tracking-wider border border-[#3291FF]/30">
              Audit Trail
            </span>
            <h1 className="text-xl font-bold text-[#FFFFFF] tracking-tight">
              Code Quality History & Trend Analysis
            </h1>
          </div>
          <p className="text-xs text-[#8F8F8F] mt-1">
            Track code quality progression over time, review defect distributions, and audit all past multi-agent inspections.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fetchHistory}
            disabled={refreshing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#141414] hover:bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>

          <Link
            href="/"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#3291FF] hover:bg-[#0070F3] text-[#FFFFFF] text-xs font-mono font-semibold transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Submission</span>
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-[#3291FF] animate-spin" />
          <p className="text-xs font-mono text-[#8F8F8F]">Loading Review Ledger...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Quality Progression Chart */}
          <QualityTrendChart reviews={reviews} />

          {/* Review Ledger Table */}
          <HistoryTable reviews={reviews} />
        </div>
      )}
    </div>
  );
}
