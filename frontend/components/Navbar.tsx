"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { 
  Code2, 
  History, 
  BookOpen, 
  LogIn, 
  LogOut, 
  Cpu,
  User as UserIcon,
  ChevronDown
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const { user, signOut, signInDemo } = useAuth();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  useEffect(() => {
    let mounted = true;
    const checkHealth = () => {
      api
        .getHealth()
        .then(() => {
          if (mounted) setBackendOnline(true);
        })
        .catch(() => {
          if (mounted) setBackendOnline(false);
        });
    };

    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const navLinks = [
    { href: "/", label: "Workspace", icon: Code2 },
    { href: "/history", label: "History Ledger", icon: History },
    { href: "/rules", label: "Team Rules", icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#0A0A0A]/90 backdrop-blur-md border-b border-[#262626]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center space-x-6">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="w-8 h-8 rounded bg-[#141414] border border-[#262626] flex items-center justify-center text-[#3291FF] group-hover:border-[#3291FF] transition-colors">
              <Cpu className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-mono text-xs font-semibold tracking-wider text-[#FFFFFF] uppercase">
                24/7 Code Reviewer
              </span>
              <span className="text-[10px] text-[#8F8F8F] font-mono tracking-tight">
                7-Agent AI Pipeline
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 pl-4 border-l border-[#262626]">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition-all ${
                    isActive
                      ? "bg-[#1A1A1A] text-[#FFFFFF] border border-[#3D3D3D]"
                      : "text-[#8F8F8F] hover:text-[#EBEBEB] hover:bg-[#141414]"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Section: System Health & User Controls */}
        <div className="flex items-center space-x-3">
          {/* Health Status Indicator */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#141414] border border-[#262626] text-[11px] font-mono">
            {backendOnline === null ? (
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            ) : backendOnline ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="text-emerald-400">Backend Ready</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-red-400" />
                <span className="text-red-400">API Offline</span>
              </>
            )}
          </div>

          {/* Auth Controls */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center space-x-2 px-3 py-1.5 rounded bg-[#141414] border border-[#262626] hover:border-[#3D3D3D] text-xs transition-colors"
              >
                <div className="w-5 h-5 rounded-full bg-[#3291FF]/20 border border-[#3291FF]/40 flex items-center justify-center text-[#3291FF]">
                  <UserIcon className="w-3 h-3" />
                </div>
                <span className="text-[#EBEBEB] font-medium max-w-[120px] truncate">
                  {user.displayName || user.email?.split("@")[0]}
                </span>
                {user.isDemo && (
                  <span className="px-1.5 py-0.5 rounded bg-[#3291FF]/10 text-[#3291FF] text-[9px] font-mono uppercase">
                    Demo
                  </span>
                )}
                <ChevronDown className="w-3 h-3 text-[#8F8F8F]" />
              </button>

              {userDropdownOpen && (
                <div 
                  className="absolute right-0 mt-2 w-48 rounded bg-[#141414] border border-[#262626] shadow-2xl py-1 text-xs z-50"
                  onMouseLeave={() => setUserDropdownOpen(false)}
                >
                  <div className="px-3 py-2 border-b border-[#262626]">
                    <p className="text-[#EBEBEB] font-medium truncate">{user.displayName}</p>
                    <p className="text-[11px] text-[#8F8F8F] font-mono truncate">{user.email}</p>
                  </div>
                  <button
                    onClick={() => {
                      setUserDropdownOpen(false);
                      signOut();
                    }}
                    className="w-full text-left flex items-center space-x-2 px-3 py-2 text-red-400 hover:bg-[#1A1A1A] transition-colors"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                onClick={signInDemo}
                className="px-3 py-1.5 rounded bg-[#141414] border border-[#3291FF]/50 text-[#3291FF] hover:bg-[#3291FF]/10 text-xs font-mono transition-colors"
              >
                Instant Demo
              </button>
              <Link
                href="/login"
                className="flex items-center space-x-1 px-3 py-1.5 rounded bg-[#FFFFFF] text-[#000000] hover:bg-[#EBEBEB] text-xs font-medium transition-colors"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
