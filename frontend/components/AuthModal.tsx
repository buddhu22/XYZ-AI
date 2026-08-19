"use client";

import React, { useState } from "react";
import { loginUser, UserInfo } from "@/lib/auth";

interface AuthModalProps {
  role: string;
  onSuccess: (user: UserInfo, token: string) => void;
  onClose: () => void;
}

// Preset development demo accounts for effortless testing
const DEMO_CREDENTIALS: Record<string, { email: string; name: string; info: string }> = {
  student: {
    email: "rahul.sharma@mail.com",
    name: "Rahul Sharma",
    info: "Student • Class 10-A (Roll STU001)",
  },
  parent: {
    email: "rajesh.sharma@mail.com",
    name: "Rajesh Sharma",
    info: "Parent of Rahul Sharma & Sneha Sharma",
  },
  teacher: {
    email: "amit.kumar@school.com",
    name: "Amit Kumar",
    info: "Teacher • Mathematics (TCH001)",
  },
  principal: {
    email: "suresh.nair@school.com",
    name: "Dr. Suresh Nair",
    info: "Principal • School Management",
  },
};

export default function AuthModal({ role, onSuccess, onClose }: AuthModalProps) {
  const normRole = role.toLowerCase();
  const demo = DEMO_CREDENTIALS[normRole] || DEMO_CREDENTIALS.student;

  const [email, setEmail] = useState(demo.email);
  const [password, setPassword] = useState("password123");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const { token, user } = await loginUser(email, password, normRole);
      setIsLoading(false);
      onSuccess(user, token);
    } catch (err: any) {
      setIsLoading(false);
      setError(err.message || "Failed to authenticate. Please check your credentials.");
    }
  };

  const handleUseDemo = () => {
    setEmail(demo.email);
    setPassword("password123");
    setError(null);
  };

  const roleColors: Record<string, string> = {
    student: "from-blue-500 to-cyan-500 border-blue-500/30",
    parent: "from-emerald-500 to-teal-500 border-emerald-500/30",
    teacher: "from-violet-500 to-purple-500 border-violet-500/30",
    principal: "from-amber-500 to-orange-500 border-amber-500/30",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/80 p-4 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-md rounded-3xl border border-zinc-800 bg-zinc-900 shadow-2xl p-6 sm:p-8">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${
                roleColors[normRole] || "from-indigo-500 to-purple-600"
              } text-xl shadow-lg`}
            >
              {normRole === "student" && "🎓"}
              {normRole === "parent" && "👨‍👩‍👧"}
              {normRole === "teacher" && "📚"}
              {normRole === "principal" && "🏫"}
            </div>
            <div>
              <h3 className="text-lg font-bold text-zinc-100 capitalize">{role} Login</h3>
              <p className="text-xs text-zinc-400">Authenticated School Portal Access</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-100 transition p-1.5 rounded-lg hover:bg-zinc-800"
          >
            ✕
          </button>
        </div>

        {/* Demo Account Box */}
        <div className="my-5 rounded-2xl border border-zinc-800 bg-zinc-950/60 p-3.5">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="font-semibold text-zinc-300">Demo Account</span>
            <button
              type="button"
              onClick={handleUseDemo}
              className="text-indigo-400 hover:text-indigo-300 font-medium transition"
            >
              Fill Credentials
            </button>
          </div>
          <p className="text-xs text-zinc-400">
            <span className="text-zinc-200 font-medium">{demo.name}</span> ({demo.info})
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1.5">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="e.g. name@school.edu"
              className="w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-indigo-500 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1.5">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-indigo-500 transition"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-xl bg-indigo-600 py-3 text-sm font-semibold text-white shadow-lg hover:bg-indigo-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Authenticating..." : `Sign in as ${role}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
