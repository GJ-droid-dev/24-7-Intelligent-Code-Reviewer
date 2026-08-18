"use client";

import React from "react";
import { ScoreBreakdown } from "@/lib/types";
import { Shield, Zap, GitMerge, TestTube2, History } from "lucide-react";

interface ScoreBreakdownChartProps {
  breakdown?: ScoreBreakdown;
}

export function ScoreBreakdownChart({ breakdown }: ScoreBreakdownChartProps) {
  if (!breakdown) return null;

  const dimensions = [
    {
      key: "security",
      name: "Security",
      weight: "30%",
      score: breakdown.security?.score ?? 0,
      rationale: breakdown.security?.rationale ?? "No major security issues identified.",
      icon: Shield,
      color: "bg-red-400",
    },
    {
      key: "performance",
      name: "Performance",
      weight: "20%",
      score: breakdown.performance?.score ?? 0,
      rationale: breakdown.performance?.rationale ?? "Evaluated query and algorithmic efficiency.",
      icon: Zap,
      color: "bg-amber-400",
    },
    {
      key: "codeQuality",
      name: "Code Quality",
      weight: "20%",
      score: breakdown.codeQuality?.score ?? 0,
      rationale: breakdown.codeQuality?.rationale ?? "Assessed structure, readability and separation of concerns.",
      icon: GitMerge,
      color: "bg-blue-400",
    },
    {
      key: "testCoverage",
      name: "Test Coverage",
      weight: "20%",
      score: breakdown.testCoverage?.score ?? 0,
      rationale: breakdown.testCoverage?.rationale ?? "Evaluated test scenarios, edge cases and failure paths.",
      icon: TestTube2,
      color: "bg-purple-400",
    },
    {
      key: "historical",
      name: "Historical Rules",
      weight: "10%",
      score: breakdown.historical?.score ?? 0,
      rationale: breakdown.historical?.rationale ?? "Checked alignment with repository guidelines and past review patterns.",
      icon: History,
      color: "bg-emerald-400",
    },
  ];

  return (
    <div className="rounded-xl bg-[#141414] border border-[#262626] p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-[#262626] pb-3">
        <h3 className="text-xs font-mono uppercase tracking-wider text-[#FFFFFF]">
          Dimension Breakdown
        </h3>
        <span className="text-[10px] font-mono text-[#8F8F8F]">
          Weighted Synthesis
        </span>
      </div>

      <div className="space-y-3.5">
        {dimensions.map((dim) => {
          const Icon = dim.icon;
          const percentage = (dim.score / 10) * 100;

          return (
            <div key={dim.key} className="space-y-1.5 group">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <Icon className="w-3.5 h-3.5 text-[#8F8F8F] group-hover:text-[#EBEBEB] transition-colors" />
                  <span className="font-medium text-[#EBEBEB]">{dim.name}</span>
                  <span className="text-[10px] font-mono text-[#8F8F8F] bg-[#1A1A1A] px-1.5 py-0.2 rounded border border-[#262626]">
                    {dim.weight}
                  </span>
                </div>
                <div className="flex items-center space-x-1.5 font-mono">
                  <span className="font-bold text-[#FFFFFF]">{dim.score}</span>
                  <span className="text-[10px] text-[#8F8F8F]">/10</span>
                </div>
              </div>

              {/* Progress Bar Track */}
              <div className="w-full h-2 rounded-full bg-[#1F1F1F] overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ease-out ${
                    dim.score >= 8
                      ? "bg-emerald-400"
                      : dim.score >= 6
                      ? "bg-blue-400"
                      : dim.score >= 4
                      ? "bg-amber-400"
                      : "bg-red-400"
                  }`}
                  style={{ width: `${percentage}%` }}
                />
              </div>

              {/* Rationale Excerpt */}
              <p className="text-[11px] text-[#8F8F8F] line-clamp-1 group-hover:line-clamp-none transition-all pt-0.5">
                {dim.rationale}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
