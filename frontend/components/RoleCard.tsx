/**
 * RoleCard — Placeholder card for a user role.
 *
 * Displays an icon, role title, and short description.
 * These are UI placeholders — no actual role switching or auth yet.
 */

interface RoleCardProps {
  icon: string;
  title: string;
  description: string;
  gradient: string;
  onClick: () => void;
}

export default function RoleCard({
  icon,
  title,
  description,
  gradient,
  onClick,
}: RoleCardProps) {
  return (
    <div
      onClick={onClick}
      className="group relative cursor-pointer overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 backdrop-blur-sm transition-all duration-300 hover:border-indigo-500/50 hover:bg-zinc-900/80 hover:shadow-lg hover:shadow-indigo-500/5 hover:-translate-y-1"
    >
      {/* Gradient accent */}
      <div
        className={`absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-10 ${gradient}`}
      ></div>

      {/* Content */}
      <div className="relative z-10">
        <div className="mb-4 text-4xl">{icon}</div>
        <h3 className="mb-2 text-lg font-semibold text-zinc-100">{title}</h3>
        <p className="text-sm leading-relaxed text-zinc-400">{description}</p>
        <div className="mt-4 flex items-center gap-1 text-xs font-semibold text-zinc-400 transition-colors group-hover:text-indigo-400">
          <span>Launch AI Assistant</span>
          <svg
            className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13 7l5 5m0 0l-5 5m5-5H6"
            />
          </svg>
        </div>
      </div>
    </div>
  );
}

