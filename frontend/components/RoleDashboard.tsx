"use client";

import React from "react";
import { UserInfo } from "@/lib/auth";

interface RoleDashboardProps {
  user: UserInfo;
  onOpenChat: () => void;
  onLogout: () => void;
}

export default function RoleDashboard({ user, onOpenChat, onLogout }: RoleDashboardProps) {
  const roleName = user.role.toLowerCase();

  const roleGradients: Record<string, string> = {
    student: "from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400",
    parent: "from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400",
    teacher: "from-violet-500/20 to-purple-500/20 border-violet-500/30 text-violet-400",
    principal: "from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400",
  };

  const roleIcons: Record<string, string> = {
    student: "🎓",
    parent: "👨‍👩‍👧",
    teacher: "📚",
    principal: "🏫",
  };

  return (
    <div className="w-full max-w-4xl rounded-3xl border border-zinc-800 bg-zinc-900/90 shadow-2xl p-6 sm:p-8 backdrop-blur-xl animate-fade-in my-8">
      {/* Top bar with User Profile and Logout */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-800">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-zinc-800 border border-zinc-700 text-3xl shadow-inner">
            {roleIcons[roleName] || "👤"}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-zinc-100">{user.name}</h2>
              <span
                className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider bg-gradient-to-r ${
                  roleGradients[roleName] || "from-zinc-800 to-zinc-700 border-zinc-700 text-zinc-300"
                }`}
              >
                {user.role}
              </span>
            </div>
            <p className="text-xs text-zinc-400">{user.email}</p>
          </div>
        </div>

        <button
          onClick={onLogout}
          className="flex items-center justify-center gap-2 rounded-xl border border-zinc-700 bg-zinc-800/80 px-4 py-2 text-xs font-medium text-zinc-300 hover:bg-red-500/10 hover:border-red-500/30 hover:text-red-400 transition"
        >
          <span>🚪</span> Logout
        </button>
      </div>

      {/* Role-Specific Context Cards */}
      <div className="my-6 grid gap-4 sm:grid-cols-2">
        {/* Parent Specific: Verified Linked Children */}
        {roleName === "parent" && (
          <div className="col-span-full rounded-2xl border border-emerald-500/20 bg-emerald-950/10 p-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3 flex items-center gap-2">
              <span>👨‍👧‍👦</span> Verified Linked Children (Database)
            </h3>
            {user.linked_children && user.linked_children.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {user.linked_children.map((child) => (
                  <div
                    key={child.id}
                    className="flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-950/60 px-4 py-3"
                  >
                    <div>
                      <h4 className="text-sm font-semibold text-zinc-200">{child.name}</h4>
                      <p className="text-xs text-zinc-400">
                        {child.class_name} {child.section && `• Sec ${child.section}`}{" "}
                        {child.roll_number && `• Roll ${child.roll_number}`}
                      </p>
                    </div>
                    <span className="rounded-lg bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-400">
                      ID: {child.id}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-zinc-400">No children linked to this account.</p>
            )}
          </div>
        )}

        {/* Student Specific Card */}
        {roleName === "student" && (
          <div className="rounded-2xl border border-blue-500/20 bg-blue-950/10 p-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-2 flex items-center gap-2">
              <span>🎓</span> Student Profile
            </h3>
            <p className="text-sm text-zinc-200 font-medium">Class 10 • Section A</p>
            <p className="text-xs text-zinc-400 mt-1">Roll Number: STU001 • ID: {user.student_id || user.id}</p>
          </div>
        )}

        {/* Teacher Specific Card */}
        {roleName === "teacher" && (
          <div className="rounded-2xl border border-violet-500/20 bg-violet-950/10 p-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-violet-400 mb-2 flex items-center gap-2">
              <span>📚</span> Teacher Profile
            </h3>
            <p className="text-sm text-zinc-200 font-medium">Mathematics • Class 10-A</p>
            <p className="text-xs text-zinc-400 mt-1">Employee ID: TCH001</p>
          </div>
        )}

        {/* Principal Specific Card */}
        {roleName === "principal" && (
          <div className="rounded-2xl border border-amber-500/20 bg-amber-950/10 p-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-2 flex items-center gap-2">
              <span>🏫</span> Institutional Authority
            </h3>
            <p className="text-sm text-zinc-200 font-medium">School-Wide Metrics & Management</p>
            <p className="text-xs text-zinc-400 mt-1">Principal / Administrative Control</p>
          </div>
        )}

        {/* AI Assistant Quick Start Card */}
        <div className="rounded-2xl border border-indigo-500/20 bg-indigo-950/10 p-5 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2 flex items-center gap-2">
              <span>⚡</span> Human-Like AI Assistant
            </h3>
            <p className="text-xs text-zinc-300">
              Authenticated with Role-Based Access Control and RBAC authorization.
            </p>
          </div>
          <button
            onClick={onOpenChat}
            className="mt-4 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-5 py-2.5 text-xs font-bold text-white shadow-lg hover:from-indigo-500 hover:to-purple-500 transition"
          >
            <span>💬</span> Launch XYZ AI Assistant
          </button>
        </div>
      </div>
    </div>
  );
}
