import HealthStatus from "@/components/HealthStatus";
import RoleCard from "@/components/RoleCard";

const roles = [
  {
    icon: "🎓",
    title: "Student",
    description:
      "Ask questions, check attendance, view grades, and get personalized learning support.",
    gradient: "bg-gradient-to-br from-blue-500 to-cyan-500",
  },
  {
    icon: "👨‍👩‍👧",
    title: "Parent",
    description:
      "Monitor your child's progress, attendance, and communicate with teachers seamlessly.",
    gradient: "bg-gradient-to-br from-emerald-500 to-teal-500",
  },
  {
    icon: "📚",
    title: "Teacher",
    description:
      "Manage classes, track student performance, and automate routine administrative tasks.",
    gradient: "bg-gradient-to-br from-violet-500 to-purple-500",
  },
  {
    icon: "🏫",
    title: "Principal",
    description:
      "Oversee school operations, review analytics, and manage staff and student affairs.",
    gradient: "bg-gradient-to-br from-amber-500 to-orange-500",
  },
];

export default function Home() {
  return (
    <div className="flex flex-1 flex-col">
      {/* ── Header ── */}
      <header className="sticky top-0 z-50 border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-sm font-bold text-white shadow-lg shadow-indigo-500/25">
              X
            </div>
            <span className="text-lg font-semibold tracking-tight">
              XYZ AI
            </span>
          </div>
          <HealthStatus />
        </div>
      </header>

      {/* ── Hero ── */}
      <main className="flex flex-1 flex-col items-center px-6">
        <section className="mx-auto flex w-full max-w-6xl flex-col items-center pt-24 pb-16 text-center">
          {/* Badge */}
          <div className="mb-6 rounded-full border border-zinc-800 bg-zinc-900/50 px-4 py-1.5 text-xs font-medium tracking-wide text-zinc-400 backdrop-blur-sm">
            🚀 Phase 1 — Foundation Ready
          </div>

          {/* Title */}
          <h1 className="max-w-3xl text-5xl font-bold leading-tight tracking-tight sm:text-6xl">
            Your{" "}
            <span className="animate-gradient bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Human-Like AI
            </span>{" "}
            School Assistant
          </h1>

          {/* Subtitle */}
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-zinc-400">
            An intelligent assistant for students, parents, teachers, and school
            management — powered by AI, designed for everyone.
          </p>

          {/* Divider */}
          <div className="mt-16 mb-4 flex items-center gap-4">
            <div className="h-px w-12 bg-zinc-800"></div>
            <span className="text-xs font-medium uppercase tracking-widest text-zinc-500">
              Choose your role
            </span>
            <div className="h-px w-12 bg-zinc-800"></div>
          </div>
        </section>

        {/* ── Role Cards Grid ── */}
        <section className="mx-auto w-full max-w-6xl pb-24">
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {roles.map((role) => (
              <RoleCard key={role.title} {...role} />
            ))}
          </div>
        </section>
      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-zinc-800/50 bg-zinc-950">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6 text-xs text-zinc-500">
          <span>© 2026 XYZ AI — Hackathon Assessment Project</span>
          <span>Phase 1 • Foundation & Architecture</span>
        </div>
      </footer>
    </div>
  );
}
