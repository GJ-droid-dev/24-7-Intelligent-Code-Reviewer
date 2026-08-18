"use client";

import React from "react";
import { 
  Cpu, 
  ShieldAlert, 
  Zap, 
  TestTube2, 
  History, 
  ClipboardCheck, 
  GitMerge, 
  CheckCircle2, 
  Loader2, 
  Clock, 
  AlertTriangle 
} from "lucide-react";
import { AgentStatus } from "@/lib/types";

interface AgentPipelineStatusProps {
  agentStatuses?: AgentStatus[];
  isAnalyzing?: boolean;
}

export const AGENT_DEFINITIONS = [
  {
    id: "orchestrator",
    name: "Orchestrator Agent",
    icon: Cpu,
    role: "Pipeline Coordination",
    desc: "Extracts context, detects language & coordinates parallel specialist fan-out.",
  },
  {
    id: "code_quality",
    name: "Code Quality Agent",
    icon: GitMerge,
    role: "Maintainability & Clean Code",
    desc: "Evaluates structure, naming, separation of concerns & duplication.",
  },
  {
    id: "security",
    name: "Security Agent",
    icon: ShieldAlert,
    role: "Vulnerabilities & Data Privacy",
    desc: "Checks authentication, authorization, IDOR, injection & secret leakage.",
  },
  {
    id: "performance",
    name: "Performance Agent",
    icon: Zap,
    role: "Scalability & Resource Usage",
    desc: "Identifies N+1 queries, unpaginated scans, memory leaks & bottlenecks.",
  },
  {
    id: "test_edge_case",
    name: "Test & Edge-Case Agent",
    icon: TestTube2,
    role: "Test Coverage & Boundaries",
    desc: "Analyzes missing positive, negative, authorization & boundary scenarios.",
  },
  {
    id: "historical_learning",
    name: "Historical Learning Agent",
    icon: History,
    role: "Repository Pattern Matching",
    desc: "Matches current change against 25+ historical defect rules & conventions.",
  },
  {
    id: "review",
    name: "Review Agent",
    icon: ClipboardCheck,
    role: "Score Synthesis & Validation",
    desc: "Validates code grounding, deduplicates findings & computes 1–10 quality score.",
  },
];

export function AgentPipelineStatus({ agentStatuses = [], isAnalyzing = false }: AgentPipelineStatusProps) {
  const getStatusForAgent = (agentId: string): { status: string; duration?: number; error?: string } => {
    const found = agentStatuses.find(
      (s) => s.agent.toLowerCase().replace(/[\s_-]/g, "") === agentId.toLowerCase().replace(/[\s_-]/g, "")
    );
    if (found) {
      return { status: found.status, duration: found.durationMs, error: found.error };
    }
    if (isAnalyzing) {
      return { status: "running" };
    }
    return { status: "pending" };
  };

  return (
    <div className="rounded-lg bg-[#141414] border border-[#262626] p-4 flex flex-col space-y-3">
      <div className="flex items-center justify-between border-b border-[#262626] pb-3">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-[#3291FF] animate-pulse" />
          <h3 className="text-xs font-mono font-semibold text-[#FFFFFF] uppercase tracking-wider">
            7-Agent Review Cascade
          </h3>
        </div>
        <span className="text-[10px] font-mono text-[#8F8F8F] px-2 py-0.5 rounded bg-[#1A1A1A] border border-[#262626]">
          Parallel Fan-Out
        </span>
      </div>

      <div className="space-y-2">
        {AGENT_DEFINITIONS.map((agent, index) => {
          const Icon = agent.icon;
          const { status, duration, error } = getStatusForAgent(agent.id);

          return (
            <div
              key={agent.id}
              className={`flex items-start justify-between p-2.5 rounded border transition-all ${
                status === "running"
                  ? "bg-[#1A1A1A] border-[#3291FF]/60 shadow-[0_0_15px_rgba(50,145,255,0.15)]"
                  : status === "success"
                  ? "bg-[#141414] border-[#262626] hover:border-[#3D3D3D]"
                  : status === "failed"
                  ? "bg-red-950/20 border-red-900/50"
                  : "bg-[#101010] border-[#1F1F1F] opacity-70"
              }`}
            >
              <div className="flex items-start space-x-3">
                <div
                  className={`w-7 h-7 rounded flex items-center justify-center text-xs mt-0.5 ${
                    status === "running"
                      ? "bg-[#3291FF]/20 text-[#3291FF] border border-[#3291FF]/50"
                      : status === "success"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                      : status === "failed"
                      ? "bg-red-500/10 text-red-400 border border-red-500/30"
                      : "bg-[#1A1A1A] text-[#8F8F8F] border border-[#262626]"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                </div>

                <div className="flex flex-col">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-[#EBEBEB]">
                      {index + 1}. {agent.name}
                    </span>
                    <span className="text-[10px] font-mono text-[#8F8F8F]">
                      [{agent.role}]
                    </span>
                  </div>
                  <p className="text-[11px] text-[#8F8F8F] line-clamp-1 mt-0.5">
                    {agent.desc}
                  </p>
                  {error && (
                    <p className="text-[10px] text-red-400 font-mono mt-1">
                      Error: {error}
                    </p>
                  )}
                </div>
              </div>

              {/* Status Badge */}
              <div className="flex items-center space-x-1.5 ml-2 self-center">
                {status === "running" ? (
                  <span className="flex items-center space-x-1 text-[11px] font-mono text-[#3291FF]">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Active</span>
                  </span>
                ) : status === "success" ? (
                  <span className="flex items-center space-x-1 text-[11px] font-mono text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {duration ? <span>{duration}ms</span> : <span>Done</span>}
                  </span>
                ) : status === "failed" ? (
                  <span className="flex items-center space-x-1 text-[11px] font-mono text-red-400">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Failed</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-1 text-[11px] font-mono text-[#52525B]">
                    <Clock className="w-3 h-3" />
                    <span>Queued</span>
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
