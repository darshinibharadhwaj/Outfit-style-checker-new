const BASE_URL = import.meta.env.VITE_API_URL || "/api";
const TOKEN_KEY = "outfit_checker_token";

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY)
};

export class AuthError extends Error {}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = tokenStore.get();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    }
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    // FastAPI sends validation errors as a list; show a friendly message instead
    const detail =
      typeof body.detail === "string"
        ? body.detail
        : Array.isArray(body.detail)
          ? "Please check what you typed and try again."
          : `Request failed: ${res.status}`;
    if (res.status === 401 && token) {
      tokenStore.clear();
      throw new AuthError("Your session ended. Please log in again.");
    }
    throw new Error(detail);
  }
  return res.json();
}

export interface User {
  id: number;
  username: string;
  display_name: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

export interface Preferences {
  style_goal: string;
  favorite_colors: string;
  preferred_occasion: string;
  skin_tone: string;
}

export interface Tip {
  goal: string;
  title: string;
  body: string;
}

export interface AnalyzeResult {
  check_id: number;
  top_color: string;
  bottom_color: string;
  top_name: string;
  bottom_name: string;
  verdict: "good" | "ok" | "change";
  summary: string;
  harmony_label: string;
  harmony_score: number;
  detail: string;
  skin_advice: string[];
  alternatives: string[];
  accessories: string[];
  footwear: string[];
  tips: string[];
}

export interface HistoryItem {
  id: number;
  top_color_hex: string;
  bottom_color_hex: string;
  harmony_label: string;
  harmony_score: number;
  created_at: string;
}

export const api = {
  register: (username: string, password: string, display_name: string) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password, display_name })
    }),
  login: (username: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    }),
  me: () => request<User>("/auth/me"),
  getPreferences: () => request<Preferences>("/preferences"),
  updatePreferences: (prefs: Preferences) =>
    request<Preferences>("/preferences", { method: "PUT", body: JSON.stringify(prefs) }),
  getTips: (goal: string) => request<Tip[]>(`/tips?goal=${encodeURIComponent(goal)}`),
  analyze: (params: {
    image_base64: string;
    top_box: [number, number, number, number];
    bottom_box: [number, number, number, number];
  }) => request<AnalyzeResult>("/analyze", { method: "POST", body: JSON.stringify(params) }),
  getHistory: () => request<HistoryItem[]>("/history")
};
