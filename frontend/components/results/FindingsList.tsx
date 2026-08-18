"use client";

import React, { useState } from "react";
import { Finding, Severity } from "@/lib/types";
import { 
  AlertOctagon, 
  AlertTriangle, 
  Info, 
  CheckCircle, 
  Copy, 
  Check, 
  BookOpen, 
  MapPin, 
  Wrench,
  ChevronDown,
  ChevronUp,
  Filter
} from "lucide-react";

interface FindingsListProps {
  findings: Finding[];
}

export function FindingsList({ findings = [] }: FindingsListProps) {
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [selectedAgent, setSelectedAgent] = useState<string>("all");
  const [expandedFindings, setExpandedFindings] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedFindings((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleCopyFix = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filter findings
  const filteredFindings = findings.filter((f) => {
    const matchesSeverity = selectedSeverity === "all" || f.severity.toLowerCase() === selectedSeverity;
    const matchesAgent =
      selectedAgent === "all" ||
      f.agentSources.some((s) => s.toLowerCase().includes(selectedAgent.toLowerCase())) ||
      f.category.toLowerCase().includes(selectedAgent.toLowerCase());
    return matchesSeverity && matchesAgent;
  });

  const getSeverityBadge = (sev: Severity) => {
    switch (sev.toLowerCase()) {
      case "critical":
        return {
          bg: "bg-red-500/10 text-red-400 border-red-500/30",
          icon: AlertOctagon,
          label: "CRITICAL",
        };
      case "high":
        return {
          bg: "bg-orange-500/10 text-orange-400 border-orange-500/30",
          icon: AlertTriangle,
          label: "HIGH",
        };
      case "medium":
        return {
          bg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
          icon: AlertTriangle,
          label: "MEDIUM",
        };
      default:
        return {
          bg: "bg-blue-500/10 text-blue-400 border-blue-500/30",
          icon: Info,
          label: "LOW",
        };
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-[#141414] border border-[#262626]">
        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-[#8F8F8F]" />
          <span className="text-xs font-mono text-[#8F8F8F] uppercase">Filter By:</span>
          
          {/* Severity Buttons */}
          <div className="flex items-center space-x-1">
            {["all", "critical", "high", "medium", "low"].map((sev) => (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-2 py-0.5 rounded text-[11px] font-mono capitalize transition-colors ${
                  selectedSeverity === sev
                    ? "bg-[#3291FF] text-[#FFFFFF] font-semibold"
                    : "bg-[#1A1A1A] text-[#8F8F8F] hover:text-[#EBEBEB] border border-[#262626]"
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {/* Agent Filter Dropdown */}
        <div className="flex items-center space-x-2">
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="px-2.5 py-1 rounded bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF]"
          >
            <option value="all">All Agents</option>
            <option value="security">Security</option>
            <option value="performance">Performance</option>
            <option value="quality">Code Quality</option>
            <option value="test">Test Coverage</option>
            <option value="historical">Historical Rules</option>
          </select>

          <span className="text-xs font-mono text-[#8F8F8F]">
            Showing {filteredFindings.length} of {findings.length}
          </span>
        </div>
      </div>

      {/* Findings List */}
      {filteredFindings.length === 0 ? (
        <div className="rounded-xl bg-[#141414] border border-[#262626] p-8 text-center space-y-2">
          <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto" />
          <h4 className="text-sm font-semibold text-[#EBEBEB]">No Findings Match Selected Filters</h4>
          <p className="text-xs text-[#8F8F8F]">All checks in this category passed successfully.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredFindings.map((finding, idx) => {
            const badge = getSeverityBadge(finding.severity);
            const Icon = badge.icon;
            const isExpanded = expandedFindings[finding.id || idx] !== false; // expanded by default

            return (
              <div
                key={finding.id || idx}
                className="rounded-xl bg-[#141414] border border-[#262626] hover:border-[#3D3D3D] transition-all overflow-hidden"
              >
                {/* Header Row */}
                <div
                  onClick={() => toggleExpand(finding.id || String(idx))}
                  className="p-4 flex items-start justify-between cursor-pointer bg-[#141414] hover:bg-[#181818] transition-colors"
                >
                  <div className="flex items-start space-x-3">
                    <div className={`px-2 py-0.5 rounded border flex items-center space-x-1 text-[10px] font-mono font-bold mt-0.5 ${badge.bg}`}>
                      <Icon className="w-3 h-3" />
                      <span>{badge.label}</span>
                    </div>

                    <div className="space-y-1">
                      <h4 className="text-sm font-semibold text-[#FFFFFF] hover:text-[#3291FF] transition-colors">
                        {finding.title}
                      </h4>

                      <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono text-[#8F8F8F]">
                        {finding.location?.file && (
                          <span className="flex items-center space-x-1 text-[#A1A1AA]">
                            <MapPin className="w-3 h-3 text-[#3291FF]" />
                            <span>
                              {finding.location.file}
                              {finding.location.startLine ? `:L${finding.location.startLine}` : ""}
                              {finding.location.endLine ? `-${finding.location.endLine}` : ""}
                            </span>
                          </span>
                        )}

                        <span>•</span>

                        <div className="flex items-center space-x-1">
                          {finding.agentSources.map((source) => (
                            <span
                              key={source}
                              className="px-1.5 py-0.2 rounded bg-[#1F1F1F] text-[#8F8F8F] text-[10px]"
                            >
                              {source}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  <button className="text-[#8F8F8F] hover:text-[#EBEBEB] p-1">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>

                {/* Expanded Details Body */}
                {isExpanded && (
                  <div className="px-4 pb-4 pt-1 space-y-3.5 border-t border-[#222222] bg-[#101010]/80">
                    {/* Description */}
                    {finding.description && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-mono text-[#8F8F8F] uppercase tracking-wider">
                          Evidence & Analysis
                        </span>
                        <p className="text-xs text-[#EBEBEB] leading-relaxed">
                          {finding.description}
                        </p>
                      </div>
                    )}

                    {/* Code Snippet if present */}
                    {finding.location?.snippet && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-mono text-[#8F8F8F] uppercase tracking-wider">
                          Flagged Code Location
                        </span>
                        <pre className="p-3 rounded bg-[#0A0A0A] border border-[#262626] text-xs font-mono text-amber-300/90 overflow-x-auto">
                          <code>{finding.location.snippet}</code>
                        </pre>
                      </div>
                    )}

                    {/* Impact / Risk */}
                    {finding.impact && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-mono text-[#8F8F8F] uppercase tracking-wider">
                          Potential Impact
                        </span>
                        <p className="text-xs text-[#A1A1AA] leading-relaxed">
                          {finding.impact}
                        </p>
                      </div>
                    )}

                    {/* Suggested Remediation */}
                    {finding.suggestedFix && (
                      <div className="p-3.5 rounded-lg bg-[#141414] border border-[#3291FF]/30 space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-1.5 text-xs font-semibold text-[#3291FF]">
                            <Wrench className="w-3.5 h-3.5" />
                            <span>Actionable Remediation</span>
                          </div>
                          <button
                            onClick={() => handleCopyFix(finding.id || String(idx), finding.suggestedFix || "")}
                            className="flex items-center space-x-1 text-[10px] font-mono text-[#8F8F8F] hover:text-[#EBEBEB]"
                          >
                            {copiedId === (finding.id || String(idx)) ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-400" />
                                <span className="text-emerald-400">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span>Copy Fix</span>
                              </>
                            )}
                          </button>
                        </div>
                        <p className="text-xs text-[#EBEBEB] leading-relaxed font-mono whitespace-pre-wrap">
                          {finding.suggestedFix}
                        </p>
                      </div>
                    )}

                    {/* Matched Historical Rule Citation */}
                    {finding.matchedRuleId && (
                      <div className="flex items-center space-x-2 p-2.5 rounded bg-emerald-950/20 border border-emerald-900/40 text-xs">
                        <BookOpen className="w-4 h-4 text-emerald-400 shrink-0" />
                        <div className="flex items-center space-x-1.5 text-[11px] font-mono">
                          <span className="font-bold text-emerald-400">
                            Historical Rule #{finding.matchedRuleId}:
                          </span>
                          <span className="text-[#EBEBEB]">
                            Matched repository engineering convention.
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
