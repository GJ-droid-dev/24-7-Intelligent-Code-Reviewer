"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Review } from "@/lib/types";
import { Search, ChevronRight } from "lucide-react";

interface HistoryTableProps {
  reviews: Review[];
}

export function HistoryTable({ reviews = [] }: HistoryTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLang, setSelectedLang] = useState("all");

  const filteredReviews = reviews.filter((r) => {
    const matchesSearch =
      (r.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.reviewId || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.description || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesLang = selectedLang === "all" || r.language.toLowerCase() === selectedLang.toLowerCase();
    return matchesSearch && matchesLang;
  });

  const getScoreBadge = (score?: number) => {
    if (score === undefined) return null;
    if (score >= 9) {
      return (
        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          {score}/10
        </span>
      );
    }
    if (score >= 7) {
      return (
        <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-xs font-mono font-bold">
          {score}/10
        </span>
      );
    }
    if (score >= 5) {
      return (
        <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-mono font-bold">
          {score}/10
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30 text-xs font-mono font-bold">
        {score}/10
      </span>
    );
  };

  return (
    <div className="rounded-xl bg-[#141414] border border-[#262626] overflow-hidden space-y-4 p-5">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#262626] pb-4">
        <div>
          <h3 className="text-xs font-mono uppercase tracking-wider text-[#FFFFFF]">
            Review Ledger & Audit Trail
          </h3>
          <p className="text-[11px] text-[#8F8F8F]">
            Historical archive of all automated multi-agent code inspections
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#8F8F8F] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by title or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1 rounded bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF] w-48"
            />
          </div>

          {/* Language Filter */}
          <select
            value={selectedLang}
            onChange={(e) => setSelectedLang(e.target.value)}
            className="px-2.5 py-1 rounded bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF]"
          >
            <option value="all">All Languages</option>
            <option value="python">Python</option>
            <option value="typescript">TypeScript</option>
            <option value="javascript">JavaScript</option>
            <option value="go">Go</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-[#262626] text-[#8F8F8F] font-mono text-[11px] uppercase">
              <th className="pb-3 pl-2">Review ID</th>
              <th className="pb-3">Submission Title</th>
              <th className="pb-3">Language</th>
              <th className="pb-3">Quality Score</th>
              <th className="pb-3">Findings</th>
              <th className="pb-3">Date</th>
              <th className="pb-3 pr-2 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1F1F1F]">
            {filteredReviews.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-[#8F8F8F]">
                  No reviews found matching criteria.
                </td>
              </tr>
            ) : (
              filteredReviews.map((review) => (
                <tr
                  key={review.reviewId}
                  className="hover:bg-[#1A1A1A] transition-colors group"
                >
                  <td className="py-3.5 pl-2 font-mono text-[#3291FF]">
                    {review.reviewId.slice(0, 8)}...
                  </td>
                  <td className="py-3.5 font-medium text-[#FFFFFF] max-w-[220px] truncate">
                    {review.title || "Code Inspection"}
                  </td>
                  <td className="py-3.5 font-mono text-[#8F8F8F] capitalize">
                    {review.language}
                  </td>
                  <td className="py-3.5">
                    {getScoreBadge(review.overallScore)}
                  </td>
                  <td className="py-3.5 font-mono text-[#8F8F8F]">
                    {review.findings?.length ?? 0} issues
                  </td>
                  <td className="py-3.5 text-[#8F8F8F] font-mono text-[11px]">
                    {new Date(review.submittedAt).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </td>
                  <td className="py-3.5 pr-2 text-right">
                    <Link
                      href={`/reviews/${review.reviewId}`}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-[#1A1A1A] group-hover:bg-[#3291FF] text-[#EBEBEB] group-hover:text-[#FFFFFF] text-[11px] font-mono transition-colors"
                    >
                      <span>View Report</span>
                      <ChevronRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
