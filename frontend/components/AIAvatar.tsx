"use client";

import React from "react";

export type AvatarState = "IDLE" | "LISTENING" | "THINKING" | "SPEAKING" | "ERROR";

interface AIAvatarProps {
  state: AvatarState;
}

export default function AIAvatar({ state }: AIAvatarProps) {
  // Determine ring color and animations based on current state
  const getStateStyles = () => {
    switch (state) {
      case "LISTENING":
        return {
          ringColor: "border-emerald-500 shadow-emerald-500/20",
          bgColor: "bg-gradient-to-br from-emerald-500 to-teal-600",
          glowColor: "bg-emerald-500/20",
          icon: "🎙️",
          animation: "animate-pulse scale-105",
        };
      case "THINKING":
        return {
          ringColor: "border-indigo-500 shadow-indigo-500/20",
          bgColor: "bg-gradient-to-br from-indigo-500 to-purple-600",
          glowColor: "bg-indigo-500/20",
          icon: "🧠",
          animation: "animate-spin",
        };
      case "SPEAKING":
        return {
          ringColor: "border-cyan-500 shadow-cyan-500/20",
          bgColor: "bg-gradient-to-br from-cyan-500 to-blue-600",
          glowColor: "bg-cyan-500/20",
          icon: "🗣️",
          animation: "animate-bounce",
        };
      case "ERROR":
        return {
          ringColor: "border-red-500 shadow-red-500/20",
          bgColor: "bg-gradient-to-br from-red-500 to-pink-600",
          glowColor: "bg-red-500/20",
          icon: "⚠️",
          animation: "animate-pulse",
        };
      case "IDLE":
      default:
        return {
          ringColor: "border-zinc-700 shadow-zinc-950/50",
          bgColor: "bg-zinc-800",
          glowColor: "bg-zinc-800/10",
          icon: "🤖",
          animation: "animate-none",
        };
    }
  };

  const styles = getStateStyles();

  return (
    <div className="flex flex-col items-center justify-center py-6">
      <div className="relative flex h-28 w-28 items-center justify-center">
        {/* Glow effect outer ring */}
        <div
          className={`absolute inset-0 -m-2 rounded-full blur-xl transition-all duration-500 ${styles.glowColor}`}
        ></div>

        {/* Pulse scale rings when listening or speaking */}
        {(state === "LISTENING" || state === "SPEAKING") && (
          <>
            <div className="absolute inset-0 -m-4 animate-ping rounded-full border border-cyan-500/20 opacity-30"></div>
            <div className="absolute inset-0 -m-2 animate-pulse rounded-full border border-cyan-500/40 opacity-50"></div>
          </>
        )}

        {/* Inner core */}
        <div
          className={`relative z-10 flex h-24 w-24 items-center justify-center rounded-full border-4 shadow-xl transition-all duration-500 ${styles.ringColor} ${styles.bgColor}`}
        >
          {/* Animated icon */}
          <div className={`text-4xl transition-all duration-300 ${styles.animation}`}>
            {styles.icon}
          </div>
        </div>
      </div>

      {/* State label */}
      <span className="mt-4 text-xs font-semibold tracking-widest text-zinc-500 uppercase">
        AI Status: <span className="text-zinc-300">{state}</span>
      </span>
    </div>
  );
}
