"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";

/**
 * HealthStatus — Displays backend connectivity status.
 *
 * Calls GET /health on mount and shows a colored indicator
 * with "Backend Connected" or "Backend Disconnected".
 */
export default function HealthStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [version, setVersion] = useState<string>("");

  useEffect(() => {
    async function check() {
      const health = await checkHealth();
      if (health && health.status === "healthy") {
        setIsConnected(true);
        setVersion(health.version);
      } else {
        setIsConnected(false);
      }
    }

    check();

    // Re-check every 30 seconds
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  if (isConnected === null) {
    return (
      <div className="flex items-center gap-2 rounded-full bg-zinc-800/60 px-4 py-2 text-sm backdrop-blur-sm">
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-yellow-400 opacity-75"></span>
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-yellow-500"></span>
        </span>
        <span className="text-zinc-400">Checking connection...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 rounded-full bg-zinc-800/60 px-4 py-2 text-sm backdrop-blur-sm">
      <span className="relative flex h-2.5 w-2.5">
        {isConnected && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
        )}
        <span
          className={`relative inline-flex h-2.5 w-2.5 rounded-full ${
            isConnected ? "bg-emerald-500" : "bg-red-500"
          }`}
        ></span>
      </span>
      <span className={isConnected ? "text-emerald-400" : "text-red-400"}>
        {isConnected ? "Backend Connected" : "Backend Disconnected"}
      </span>
      {isConnected && version && (
        <span className="text-zinc-500">v{version}</span>
      )}
    </div>
  );
}
