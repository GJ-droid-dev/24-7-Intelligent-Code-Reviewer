"use client";

import React, { useState } from "react";
import { Info, Sparkles } from "lucide-react";

interface FieldTooltipProps {
  title: string;
  description: string;
  agentImpact: string;
  align?: "left" | "right" | "center";
}

export function FieldTooltip({
  title,
  description,
  agentImpact,
  align = "left",
}: FieldTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);

  const alignmentClasses = {
    left: "left-0",
    right: "right-0",
    center: "left-1/2 -translate-x-1/2",
  }[align];

  return (
    <div 
      className="relative inline-flex items-center group"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <button
        type="button"
        aria-label={`Information about ${title}`}
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center justify-center p-0.5 rounded-full text-[#71717A] hover:text-[#3291FF] focus:text-[#3291FF] focus:outline-none transition-colors ml-1.5 cursor-help"
      >
        <Info className="w-3.5 h-3.5" />
      </button>

      {/* Floating Context Card */}
      <div
        className={`absolute bottom-full mb-2 ${alignmentClasses} z-50 w-72 md:w-80 p-3.5 rounded-xl bg-[#141414]/95 backdrop-blur-md border border-[#2E2E33] shadow-2xl transition-all duration-150 origin-bottom ${
          isOpen
            ? "opacity-100 scale-100 pointer-events-auto"
            : "opacity-0 scale-95 pointer-events-none"
        }`}
      >
        {/* Header with Title & Badge */}
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#262626]">
          <div className="flex items-center space-x-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#3291FF]" />
            <span className="text-xs font-mono font-semibold text-[#FFFFFF] tracking-tight">
              {title}
            </span>
          </div>
          <span className="text-[9px] font-mono uppercase tracking-wider text-[#3291FF] bg-[#3291FF]/10 px-1.5 py-0.5 rounded border border-[#3291FF]/20">
            Pipeline Context
          </span>
        </div>

        {/* Description */}
        <p className="text-[11px] text-[#A1A1AA] leading-relaxed mb-2.5">
          {description}
        </p>

        {/* How Agents Use This */}
        <div className="p-2 rounded-lg bg-[#0A0A0A] border border-[#262626] flex items-start space-x-2 text-[10px] text-[#8F8F8F]">
          <Sparkles className="w-3.5 h-3.5 text-[#3291FF] shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-mono font-semibold text-[#EBEBEB] block uppercase tracking-wider text-[9px]">
              AI Agent Impact:
            </span>
            <span className="leading-normal text-[#D4D4D8]">
              {agentImpact}
            </span>
          </div>
        </div>

        {/* Pointer Arrow */}
        <div className={`absolute -bottom-1.5 ${align === "left" ? "left-3" : align === "right" ? "right-3" : "left-1/2 -translate-x-1/2"} w-3 h-3 bg-[#141414] border-b border-r border-[#2E2E33] rotate-45`} />
      </div>
    </div>
  );
}
