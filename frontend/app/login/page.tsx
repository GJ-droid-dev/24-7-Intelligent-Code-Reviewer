"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Cpu, Lock, Mail, ArrowRight, Sparkles, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { signInWithGoogle, signInWithEmail, signUpWithEmail, signInDemo } = useAuth();

  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await signUpWithEmail(email, password);
      } else {
        await signInWithEmail(email, password);
      }
      router.push("/");
    } catch (err: unknown) {
      console.error("Auth Error:", err);
      const message = err instanceof Error ? err.message : "Authentication failed. You can use Instant Demo mode below.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    try {
      setError(null);
      setLoading(true);
      await signInWithGoogle();
      router.push("/");
    } catch (err: unknown) {
      console.error("Google Sign-In Error:", err);
      setError("Google Sign-In provider is not enabled in Firebase Console for this project. Please click 'Instant Demo Access (Staff Eng)' above to test all features immediately.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = () => {
    signInDemo();
    router.push("/");
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center py-8">
      <div className="w-full max-w-md rounded-2xl bg-[#141414] border border-[#262626] p-8 shadow-2xl space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-[#1A1A1A] border border-[#262626] flex items-center justify-center text-[#3291FF] mx-auto shadow-inner">
            <Cpu className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-[#FFFFFF] tracking-tight">
            {isRegister ? "Create Reviewer Account" : "Precision Editorial Auth"}
          </h2>
          <p className="text-xs text-[#8F8F8F]">
            Sign in to submit code changes and persist automated review history.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/30 border border-red-900/50 flex items-start space-x-2 text-xs text-red-400 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Instant Demo CTA Button */}
        <button
          type="button"
          onClick={handleDemo}
          className="w-full py-2.5 px-4 rounded-lg bg-[#3291FF]/10 hover:bg-[#3291FF]/20 border border-[#3291FF]/40 text-[#3291FF] text-xs font-mono font-semibold transition-all flex items-center justify-center space-x-2"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Instant Demo Access (Staff Eng)</span>
        </button>

        <div className="flex items-center space-x-3 text-xs text-[#52525B]">
          <div className="flex-1 h-px bg-[#262626]" />
          <span className="font-mono text-[10px] uppercase">Or Continue With</span>
          <div className="flex-1 h-px bg-[#262626]" />
        </div>

        {/* Google OAuth */}
        <button
          type="button"
          onClick={handleGoogle}
          disabled={loading}
          className="w-full py-2.5 px-4 rounded-lg bg-[#1A1A1A] hover:bg-[#222222] border border-[#262626] text-xs text-[#EBEBEB] font-medium transition-colors flex items-center justify-center space-x-2"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path
              fill="#EA4335"
              d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.9C6.2 7.3 8.8 5 12 5z"
            />
            <path
              fill="#4285F4"
              d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"
            />
            <path
              fill="#FBBC05"
              d="M5.3 14.7c-.2-.7-.4-1.5-.4-2.3 0-.8.2-1.6.4-2.3L1.6 7.2C.6 9.2 0 11.5 0 14s.6 4.8 1.6 6.8l3.7-2.9c0-.7 0-1.5 0-3.2z"
            />
            <path
              fill="#34A853"
              d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.2 0-5.8-2.3-6.7-5.3L1.6 16c1.9 3.8 5.8 6.4 10.4 6.4z"
            />
          </svg>
          <span>Sign in with Google</span>
        </button>

        {/* Email/Password Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-[#8F8F8F] uppercase">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-3.5 h-3.5 text-[#8F8F8F] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="developer@company.com"
                className="w-full pl-8 pr-3 py-2 rounded bg-[#0A0A0A] border border-[#262626] text-xs text-[#EBEBEB] focus:outline-none focus:border-[#3291FF]"
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-mono text-[#8F8F8F] uppercase">
              Password
            </label>
            <div className="relative">
              <Lock className="w-3.5 h-3.5 text-[#8F8F8F] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-8 pr-3 py-2 rounded bg-[#0A0A0A] border border-[#262626] text-xs text-[#EBEBEB] focus:outline-none focus:border-[#3291FF]"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-[#FFFFFF] hover:bg-[#EBEBEB] text-[#000000] font-semibold text-xs transition-colors flex items-center justify-center space-x-2"
          >
            <span>{isRegister ? "Create Account" : "Sign In with Email"}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Toggle Register/Login */}
        <div className="text-center pt-2 border-t border-[#262626]">
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="text-xs text-[#8F8F8F] hover:text-[#3291FF] transition-colors"
          >
            {isRegister ? "Already have an account? Sign in" : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
}
