"use client";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChildInfo {
  id: number;
  name: string;
  class_name?: string;
  section?: string;
  roll_number?: string;
}

export interface UserInfo {
  id: number;
  name: string;
  email: string;
  role: "student" | "parent" | "teacher" | "principal";
  student_id?: number;
  parent_id?: number;
  teacher_id?: number;
  linked_children?: ChildInfo[];
}

export interface AuthState {
  token: string | null;
  user: UserInfo | null;
}

const TOKEN_KEY = "xyz_ai_token";
const USER_KEY = "xyz_ai_user";

export function getStoredAuth(): AuthState {
  if (typeof window === "undefined") {
    return { token: null, user: null };
  }
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const userStr = localStorage.getItem(USER_KEY);
    const user = userStr ? JSON.parse(userStr) : null;
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
}

export function setStoredAuth(token: string, user: UserInfo): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (e) {
    console.error("Failed to store auth:", e);
  }
}

export function clearStoredAuth(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (e) {
    console.error("Failed to clear auth:", e);
  }
}

export async function loginUser(
  email: string,
  password: string,
  role?: string
): Promise<{ token: string; user: UserInfo }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, role: role?.toLowerCase() }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(err.detail || `Login error (${response.status})`);
  }

  const data = await response.json();
  const token = data.access_token;
  const user = data.user;

  setStoredAuth(token, user);
  return { token, user };
}

export async function fetchCurrentUser(token: string): Promise<UserInfo> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    clearStoredAuth();
    throw new Error("Session expired. Please log in again.");
  }

  return response.json();
}
