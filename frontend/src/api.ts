const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export interface User {
  id: number;
  display_name: string;
}

export interface Preferences {
  style_goal: string;
  favorite_colors: string;
  preferred_occasion: string;
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
  harmony_label: string;
  harmony_score: number;
  detail: string;
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
  createUser: (display_name: string) =>
    request<User>("/users", { method: "POST", body: JSON.stringify({ display_name }) }),
  getUser: (id: number) => request<User>(`/users/${id}`),
  getPreferences: (userId: number) => request<Preferences>(`/users/${userId}/preferences`),
  updatePreferences: (userId: number, prefs: Preferences) =>
    request<Preferences>(`/users/${userId}/preferences`, {
      method: "PUT",
      body: JSON.stringify(prefs)
    }),
  getTips: (goal: string) => request<Tip[]>(`/tips?goal=${encodeURIComponent(goal)}`),
  analyze: (params: {
    user_id: number;
    image_base64: string;
    top_box: [number, number, number, number];
    bottom_box: [number, number, number, number];
  }) => request<AnalyzeResult>("/analyze", { method: "POST", body: JSON.stringify(params) }),
  getHistory: (userId: number) => request<HistoryItem[]>(`/history/${userId}`)
};
