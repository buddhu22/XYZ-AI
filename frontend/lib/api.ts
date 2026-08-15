/**
 * XYZ AI — API Client Utility
 *
 * Centralized API communication layer for the FastAPI backend.
 * All backend calls go through this module.
 */

import { HealthResponse } from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Check backend health status.
 * Returns the health response or null if the backend is unreachable.
 */
export async function checkHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch {
    return null;
  }
}
