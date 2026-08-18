"use client";

import React from "react";
import { ScoreBreakdown, ScoreDimension } from "@/lib/types";
import { Shield, Zap, GitMerge, TestTube2, History } from "lucide-react";

interface ScoreBreakdownChartProps {
  breakdown?: ScoreBreakdown;
}

export function ScoreBreakdownChart({ breakdown }: ScoreBreakdownChartProps) {
  if (!breakdown) return null;

  const extractScore = (val?: number | ScoreDimension): number => {
    if (typeof val === "number") return val;
    if (val && typeof val.score === "number") return val.score;
    return 7;
  };

  const extractRationale = (val?: number | ScoreDimension, fallback: string = ""): string => {
    if (val && typeof val === "object" && val.rationale) return val.rationale;
    return fallback;
  };

  const dimensions = [
    {
      key: "security",
      name: "Security",
      weight: "30%",
      score: extractScore(breakdown.security),
      rationale: extractRationale(breakdown.security, "Evaluated authentication, injection, secrets & data privacy."),
      icon: Shield,
      color: "bg-red-400",
    },
    {
      key: "performance",
      name: "Performance",
      weight: "20%",
      score: extractScore(breakdown.performance),
      rationale: extractRationale(breakdown.performance, "Evaluated query and algorithmic efficiency."),
      icon: Zap,
      color: "bg-amber-400",
    },
    {
      key: "codeQuality",
      name: "Code Quality",
      weight: "20%",
      score: extractScore(breakdown.codeQuality),
      rationale: extractRationale(breakdown.codeQuality, "Assessed structure, readability and separation of concerns."),
      icon: GitMerge,
      color: "bg-blue-400",
    },
    {
      key: "testCoverage",
      name: "Test Coverage",
      weight: "20%",
      score: extractScore(breakdown.testCoverage),
      rationale: extractRationale(breakdown.testCoverage, "Evaluated test scenarios, edge cases and failure paths."),
      icon: TestTube2,
      color: "bg-purple-400",
    },
    {
      key: "historical",
      name: "Historical Rules",
      weight: "10%",
      score: extractScore(breakdown.historical),
      rationale: extractRationale(breakdown.historical, "Checked alignment with repository guidelines and past review patterns."),
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
