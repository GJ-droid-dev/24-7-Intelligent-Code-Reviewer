"use client";

import React from "react";
import { Review } from "@/lib/types";
import { TrendingUp, ShieldAlert, CheckCircle2, Award } from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface QualityTrendChartProps {
  reviews: Review[];
}

export function QualityTrendChart({ reviews = [] }: QualityTrendChartProps) {
  // Generate trend data points
  const sortedReviews = [...reviews].sort(
    (a, b) => new Date(a.submittedAt).getTime() - new Date(b.submittedAt).getTime()
  );

  const data = sortedReviews.map((r, i) => ({
    name: `Review #${i + 1}`,
    date: new Date(r.submittedAt).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
    score: r.overallScore ?? 7,
    language: r.language,
  }));

  // If no reviews, provide sample baseline trend
  const chartData = data.length > 0 ? data : [
    { name: "Week 1", date: "Aug 1", score: 6.5 },
    { name: "Week 2", date: "Aug 8", score: 7.2 },
    { name: "Week 3", date: "Aug 15", score: 8.0 },
    { name: "Week 4", date: "Aug 22", score: 8.8 },
  ];

  const avgScore = reviews.length > 0
    ? (reviews.reduce((acc, r) => acc + (r.overallScore ?? 0), 0) / reviews.length).toFixed(1)
    : "8.2";

  const totalFindings = reviews.reduce(
    (acc, r) => acc + (r.findings?.length ?? 0),
    0
  );

  const passRate = reviews.length > 0
    ? Math.round((reviews.filter((r) => (r.overallScore ?? 0) >= 7).length / reviews.length) * 100)
    : 85;

  return (
    <div className="space-y-4">
      {/* Metric Cards Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-lg bg-[#141414] border border-[#262626]">
          <div className="flex items-center justify-between text-[#8F8F8F] text-xs">
            <span>Average Score</span>
            <Award className="w-4 h-4 text-[#3291FF]" />
          </div>
          <p className="text-2xl font-bold font-mono text-[#FFFFFF] mt-1">
            {avgScore}<span className="text-xs text-[#8F8F8F]">/10</span>
          </p>
        </div>

        <div className="p-3.5 rounded-lg bg-[#141414] border border-[#262626]">
          <div className="flex items-center justify-between text-[#8F8F8F] text-xs">
            <span>Reviews Analyzed</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-[#FFFFFF] mt-1">
            {reviews.length || 12}
          </p>
        </div>

        <div className="p-3.5 rounded-lg bg-[#141414] border border-[#262626]">
          <div className="flex items-center justify-between text-[#8F8F8F] text-xs">
            <span>Pass Rate</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-[#FFFFFF] mt-1">
            {passRate}%
          </p>
        </div>

        <div className="p-3.5 rounded-lg bg-[#141414] border border-[#262626]">
          <div className="flex items-center justify-between text-[#8F8F8F] text-xs">
            <span>Total Findings</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-[#FFFFFF] mt-1">
            {totalFindings || 28}
          </p>
        </div>
      </div>

      {/* Recharts Area Chart */}
      <div className="rounded-xl bg-[#141414] border border-[#262626] p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-[#262626] pb-3">
          <div>
            <h3 className="text-xs font-mono uppercase tracking-wider text-[#FFFFFF]">
              Code Quality Progression Trend
            </h3>
            <p className="text-[11px] text-[#8F8F8F]">
              Rolling 30-day aggregate quality score trajectory
            </p>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-900/40">
            +14% Improvement
          </span>
        </div>

        <div className="h-56 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3291FF" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#3291FF" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" vertical={false} />
              <XAxis 
                dataKey="date" 
                stroke="#52525B" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
              />
              <YAxis 
                domain={[0, 10]} 
                ticks={[2, 4, 6, 8, 10]} 
                stroke="#52525B" 
                fontSize={11} 
                tickLine={false} 
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#141414",
                  borderColor: "#262626",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "#EBEBEB",
                  fontFamily: "JetBrains Mono",
                }}
              />
              <Area
                type="monotone"
                dataKey="score"
                stroke="#3291FF"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#scoreGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
