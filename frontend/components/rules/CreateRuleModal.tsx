"use client";

import React, { useState } from "react";
import { 
  X, 
  BookOpen, 
  Sparkles, 
  Loader2, 
  AlertCircle,
  CheckCircle2,
  Shield,
  Zap,
  Code2,
  Eye,
  CheckSquare,
  Layers,
  HelpCircle
} from "lucide-react";
import { HistoricalRule } from "@/lib/types";

interface CreateRuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (rule: { type: string; description: string }) => Promise<HistoricalRule | void>;
}

const CATEGORIES = [
  { id: "security", label: "Security", badge: "bg-red-500/10 text-red-400 border-red-500/30", icon: Shield, example: "Never interpolate raw user input directly into database queries." },
  { id: "performance", label: "Performance", badge: "bg-amber-500/10 text-amber-400 border-amber-500/30", icon: Zap, example: "Cache repeated external API lookups within request lifecycle." },
  { id: "formatting", label: "Formatting", badge: "bg-blue-500/10 text-blue-400 border-blue-500/30", icon: Code2, example: "Avoid single-character variable names — use descriptive identifiers." },
  { id: "readability", label: "Readability", badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30", icon: Eye, example: "Limit function cyclomatic complexity and nest depth to max 3 levels." },
  { id: "testing", label: "Testing", badge: "bg-purple-500/10 text-purple-400 border-purple-500/30", icon: CheckSquare, example: "All state-modifying endpoints must include negative unauthorized test cases." },
  { id: "architecture", label: "Architecture", badge: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30", icon: Layers, example: "Database access must remain encapsulated within repository layer." },
  { id: "general", label: "General", badge: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30", icon: HelpCircle, example: "Follow standard project logging conventions and exception handlers." },
];

export function CreateRuleModal({ isOpen, onClose, onSubmit }: CreateRuleModalProps) {
  const [type, setType] = useState("security");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const currentCategory = CATEGORIES.find((c) => c.id === type) || CATEGORIES[0];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const trimmed = description.trim();
    if (trimmed.length < 5) {
      setError("Rule description must be at least 5 characters long.");
      return;
    }

    try {
      setLoading(true);
      await onSubmit({ type, description: trimmed });
      setDescription("");
      setType("security");
      onClose();
    } catch (err: unknown) {
      console.error("Failed to create rule:", err);
      const msg = err instanceof Error ? err.message : "Failed to create rule. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="w-full max-w-lg rounded-2xl bg-[#141414] border border-[#262626] shadow-2xl overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#262626] bg-[#0A0A0A]/50">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#3291FF]/10 border border-[#3291FF]/30 flex items-center justify-center text-[#3291FF]">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-mono font-bold text-[#FFFFFF] tracking-tight">
                Create Repository Rule
              </h3>
              <p className="text-[11px] text-[#8F8F8F]">
                Add engineering convention for the Historical Learning Agent
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-[#8F8F8F] hover:text-[#FFFFFF] hover:bg-[#1F1F1F] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="p-3 rounded-lg bg-red-950/30 border border-red-900/50 flex items-start space-x-2 text-xs text-red-400 font-mono">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          {/* Auto-Assigned ID Banner */}
          <div className="p-3 rounded-xl bg-[#0A0A0A] border border-[#262626] flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-[#8F8F8F] font-mono">
              <Sparkles className="w-4 h-4 text-[#3291FF]" />
              <span>Rule ID:</span>
            </div>
            <span className="px-2.5 py-0.5 rounded text-[11px] font-mono text-[#3291FF] bg-[#3291FF]/10 border border-[#3291FF]/30">
              Auto-Assigned on Save
            </span>
          </div>

          {/* Category Dropdown */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-mono text-[#8F8F8F] uppercase tracking-wider block">
              Rule Category
            </label>
            <div className="relative">
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg bg-[#0A0A0A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF] appearance-none cursor-pointer"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id} className="bg-[#141414] text-[#EBEBEB]">
                    {cat.label}
                  </option>
                ))}
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <span className={`px-2 py-0.5 rounded border text-[10px] font-mono uppercase ${currentCategory.badge}`}>
                  {currentCategory.label}
                </span>
              </div>
            </div>
          </div>

          {/* Rule Description Textarea */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-mono text-[#8F8F8F] uppercase tracking-wider block">
                Engineering Convention / Rule Description
              </label>
              <span className="text-[10px] font-mono text-[#71717A]">
                {description.length} / 1000 chars
              </span>
            </div>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={`e.g. ${currentCategory.example}`}
              maxLength={1000}
              required
              className="w-full px-3.5 py-2.5 rounded-lg bg-[#0A0A0A] border border-[#262626] text-xs font-mono text-[#EBEBEB] focus:outline-none focus:border-[#3291FF] resize-none leading-relaxed"
            />
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end space-x-3 pt-2 border-t border-[#262626]">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-[#1A1A1A] hover:bg-[#222222] border border-[#262626] text-xs font-mono text-[#8F8F8F] hover:text-[#EBEBEB] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || description.trim().length < 5}
              className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-[#3291FF] hover:bg-[#0070F3] text-white text-xs font-mono font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#3291FF]/20"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Saving Rule...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Save Rule</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
