"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { HistoricalRule } from "@/lib/types";
import { RulesTable } from "@/components/rules/RulesTable";
import { Loader2, RefreshCw } from "lucide-react";

export default function RulesPage() {
  const { getIdToken, signInDemo } = useAuth();
  const [rules, setRules] = useState<HistoricalRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchRules = useCallback(async () => {
    try {
      setRefreshing(true);
      let token = await getIdToken();
      if (!token) {
        signInDemo();
        token = "mock-test-token-test-user-001";
      }

      const data = await api.getRules(token);
      setRules(data.rules || []);
    } catch (err) {
      console.error("Failed to load historical rules:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [getIdToken, signInDemo]);

  useEffect(() => {
    fetchRules();
  }, [fetchRules]);

  const handleUploadCsv = async (file: File) => {
    let token = await getIdToken();
    if (!token) {
      signInDemo();
      token = "mock-test-token-test-user-001";
    }

    await api.uploadRulesCsv(file, token);
    await fetchRules();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#262626] pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded bg-[#3291FF]/10 text-[#3291FF] text-[10px] font-mono uppercase tracking-wider border border-[#3291FF]/30">
              Knowledge Base
            </span>
            <h1 className="text-xl font-bold text-[#FFFFFF] tracking-tight">
              Historical Review Rules & Repository Guidelines
            </h1>
          </div>
          <p className="text-xs text-[#8F8F8F] mt-1">
            Rules and engineering conventions matched by the Historical Learning Agent during multi-agent pipeline execution.
          </p>
        </div>

        <button
          onClick={fetchRules}
          disabled={refreshing}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#141414] hover:bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
          <span>Refresh Rules</span>
        </button>
      </div>

      {loading ? (
        <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-[#3291FF] animate-spin" />
          <p className="text-xs font-mono text-[#8F8F8F]">Loading Historical Knowledge Base...</p>
        </div>
      ) : (
        <RulesTable rules={rules} onUploadCsv={handleUploadCsv} />
      )}
    </div>
  );
}
