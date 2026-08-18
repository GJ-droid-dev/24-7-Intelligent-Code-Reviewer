"use client";

import React, { useState } from "react";
import { HistoricalRule } from "@/lib/types";
import { BookOpen, Upload, Search, CheckCircle2 } from "lucide-react";

interface RulesTableProps {
  rules: HistoricalRule[];
  onUploadCsv?: (file: File) => Promise<void>;
}

export function RulesTable({ rules = [], onUploadCsv }: RulesTableProps) {
  const [selectedType, setSelectedType] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const filteredRules = rules.filter((r) => {
    const matchesType = selectedType === "all" || r.type.toLowerCase() === selectedType.toLowerCase();
    const matchesSearch =
      r.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const handleFileDrop = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !onUploadCsv) return;

    try {
      setUploading(true);
      await onUploadCsv(file);
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);
    } catch (err) {
      console.error("CSV Upload failed:", err);
    } finally {
      setUploading(false);
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type.toLowerCase()) {
      case "security":
        return "bg-red-500/10 text-red-400 border-red-500/30";
      case "performance":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "testing":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "formatting":
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      default:
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload CSV Dropzone Card */}
      <div className="rounded-xl bg-[#141414] border border-[#262626] p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-[#3291FF]" />
              <h3 className="text-xs font-mono font-semibold text-[#FFFFFF] uppercase tracking-wider">
                Ingest Team Review Knowledge (CSV)
              </h3>
            </div>
            <p className="text-xs text-[#8F8F8F]">
              Import repository conventions, anti-patterns, and architecture guidelines. Required schema: <code className="text-[#3291FF] font-mono">id,type,description</code>
            </p>
          </div>

          <label className="cursor-pointer inline-flex items-center space-x-2 px-4 py-2 rounded bg-[#1A1A1A] hover:bg-[#222222] border border-[#3291FF]/40 text-[#3291FF] text-xs font-mono transition-colors shrink-0">
            <Upload className="w-3.5 h-3.5" />
            <span>{uploading ? "Ingesting..." : "Upload Rules CSV"}</span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileDrop}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </div>

        {uploadSuccess && (
          <div className="mt-3 p-2 rounded bg-emerald-950/30 border border-emerald-900/40 flex items-center space-x-2 text-xs text-emerald-400 font-mono">
            <CheckCircle2 className="w-4 h-4" />
            <span>Rules successfully ingested into Historical Learning Knowledge Base!</span>
          </div>
        )}
      </div>

      {/* Rules Table Explorer */}
      <div className="rounded-xl bg-[#141414] border border-[#262626] p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#262626] pb-4">
          <div>
            <h3 className="text-xs font-mono uppercase tracking-wider text-[#FFFFFF]">
              Active Repository Rules ({filteredRules.length})
            </h3>
            <p className="text-[11px] text-[#8F8F8F]">
              Injected into the Historical Learning Agent during multi-agent pipeline execution
            </p>
          </div>

          <div className="flex items-center space-x-2">
            {/* Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#8F8F8F] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search rule descriptions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1 rounded bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF] w-52"
              />
            </div>

            {/* Type Filter */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-2.5 py-1 rounded bg-[#1A1A1A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF]"
            >
              <option value="all">All Categories</option>
              <option value="security">Security</option>
              <option value="performance">Performance</option>
              <option value="formatting">Formatting</option>
              <option value="readability">Readability</option>
              <option value="testing">Testing</option>
            </select>
          </div>
        </div>

        {/* Rules Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#262626] text-[#8F8F8F] font-mono text-[11px] uppercase">
                <th className="pb-3 pl-2 w-20">Rule ID</th>
                <th className="pb-3 w-32">Category</th>
                <th className="pb-3">Engineering Convention / Rule Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1F1F1F]">
              {filteredRules.length === 0 ? (
                <tr>
                  <td colSpan={3} className="py-8 text-center text-[#8F8F8F]">
                    No historical rules found.
                  </td>
                </tr>
              ) : (
                filteredRules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-[#1A1A1A] transition-colors">
                    <td className="py-3.5 pl-2 font-mono text-[#3291FF] font-semibold">
                      #{rule.id}
                    </td>
                    <td className="py-3.5">
                      <span className={`px-2 py-0.5 rounded border text-[10px] font-mono uppercase font-medium ${getTypeBadge(rule.type)}`}>
                        {rule.type}
                      </span>
                    </td>
                    <td className="py-3.5 text-[#EBEBEB] font-mono text-xs leading-relaxed">
                      {rule.description}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
