"use client";

import React from "react";
import { ScoreLabel, Recommendation } from "@/lib/types";
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2 } from "lucide-react";

interface ScoreGaugeProps {
  score: number;
  label?: ScoreLabel;
  recommendation?: Recommendation;
  blockingCount?: number;
}

export function ScoreGauge({
  score = 0,
  label = "Fair",
  recommendation,
  blockingCount = 0,
}: ScoreGaugeProps) {
  // Normalize score between 0 and 10
  const normalizedScore = Math.max(1, Math.min(10, score));
  const percentage = (normalizedScore / 10) * 100;
  
  // Circumference for 100 radius circle
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getScoreTheme = () => {
    if (recommendation === "safe_to_merge" || normalizedScore >= 9) {
      return {
        color: "#34D399",
        gradientId: "score-green",
        glowClass: "score-glow-high",
        badgeBg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
        label: "Production Ready",
        recText: "Safe to Merge",
        icon: ShieldCheck,
      };
    }
    if (recommendation === "merge_with_non_blocking_changes" || normalizedScore >= 7) {
      return {
        color: "#3291FF",
        gradientId: "score-blue",
        glowClass: "score-glow-mid",
        badgeBg: "bg-blue-500/10 text-blue-400 border-blue-500/30",
        label: "Good Quality",
        recText: "Merge with Non-Blocking Changes",
        icon: CheckCircle2,
      };
    }
    if (normalizedScore >= 5) {
      return {
        color: "#FF9F0A",
        gradientId: "score-amber",
        glowClass: "score-glow-mid",
        badgeBg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
        label: "Needs Improvement",
        recText: "Address Issues First",
        icon: AlertTriangle,
      };
    }
    return {
      color: "#FF453A",
      gradientId: "score-red",
      glowClass: "score-glow-low",
      badgeBg: "bg-red-500/10 text-red-400 border-red-500/30",
      label: "Critical Risks",
      recText: "Do Not Merge",
      icon: XCircle,
    };
  };

  const theme = getScoreTheme();
  const Icon = theme.icon;

  return (
    <div className={`rounded-xl bg-[#141414] border border-[#262626] p-5 flex flex-col items-center justify-center relative overflow-hidden ${theme.glowClass} transition-all`}>
      {/* Top Header */}
      <div className="w-full flex items-center justify-between border-b border-[#262626] pb-3 mb-4">
        <span className="text-[11px] font-mono uppercase tracking-wider text-[#8F8F8F]">
          Code Quality Score
        </span>
        <div className={`px-2 py-0.5 rounded border text-[10px] font-mono uppercase ${theme.badgeBg}`}>
          {label}
        </div>
      </div>

      {/* Radial Gauge SVG */}
      <div className="relative w-36 h-36 flex items-center justify-center my-2">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
          {/* Background Track */}
          <circle
            cx="60"
            cy="60"
            r={radius}
            stroke="#1F1F1F"
            strokeWidth="10"
            fill="transparent"
          />
          {/* Progress Ring */}
          <circle
            cx="60"
            cy="60"
            r={radius}
            stroke={theme.color}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Score Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-bold font-mono text-[#FFFFFF] tracking-tight">
            {normalizedScore}
          </span>
          <span className="text-[11px] font-mono text-[#8F8F8F]">
            out of 10
          </span>
        </div>
      </div>

      {/* Recommendation Bottom Banner */}
      <div className="w-full mt-3 pt-3 border-t border-[#262626] flex items-center justify-between text-xs">
        <div className="flex items-center space-x-1.5">
          <Icon className="w-4 h-4 text-[#EBEBEB]" />
          <span className="text-[#EBEBEB] font-medium">{theme.recText}</span>
        </div>
        {blockingCount > 0 && (
          <span className="text-[10px] font-mono text-red-400 bg-red-950/30 px-1.5 py-0.5 rounded border border-red-900/40">
            {blockingCount} Blocking
          </span>
        )}
      </div>
    </div>
  );
}
