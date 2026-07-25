import { useEffect, useState } from "react";
import { api, type Preferences, type AnalyzeResult, type HistoryItem } from "./api";
import WebcamPanel, { TOP_BOX, BOTTOM_BOX } from "./components/WebcamPanel";
import ResultCard from "./components/ResultCard";
import GoalPicker from "./components/GoalPicker";
import History from "./components/History";

const USER_ID_KEY = "outfit_checker_user_id";

export default function App() {
  const [userId, setUserId] = useState<number | null>(null);
  const [nameInput, setNameInput] = useState("");
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Bootstrap: load existing user from localStorage, or wait for name entry
  useEffect(() => {
    const stored = localStorage.getItem(USER_ID_KEY);
    if (stored) {
      const id = Number(stored);
      api
        .getUser(id)
        .then(() => setUserId(id))
        .catch(() => localStorage.removeItem(USER_ID_KEY));
    }
  }, []);

  useEffect(() => {
    if (userId == null) return;
    api.getPreferences(userId).then(setPrefs).catch(() => setError("Could not load your preferences."));
    api.getHistory(userId).then(setHistory).catch(() => {});
  }, [userId]);

  const createProfile = async () => {
    if (!nameInput.trim()) return;
    try {
      const user = await api.createUser(nameInput.trim());
      localStorage.setItem(USER_ID_KEY, String(user.id));
      setUserId(user.id);
    } catch {
      setError("Could not reach the API. Is the backend running on http://localhost:8000?");
    }
  };

  const updatePrefs = async (next: Preferences) => {
    setPrefs(next);
    if (userId != null) {
      try {
        await api.updatePreferences(userId, next);
      } catch {
        setError("Could not save preferences.");
      }
    }
  };

  const handleCapture = async (imageBase64: string) => {
    if (userId == null) return;
    setBusy(true);
    setError(null);
    try {
      const res = await api.analyze({
        user_id: userId,
        image_base64: imageBase64,
        top_box: TOP_BOX,
        bottom_box: BOTTOM_BOX
      });
      setResult(res);
      const updatedHistory = await api.getHistory(userId);
      setHistory(updatedHistory);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong analyzing the photo.");
    } finally {
      setBusy(false);
    }
  };

  if (userId == null) {
    return (
      <div className="min-h-screen flex items-center justify-center text-ink font-body px-6">
        <div className="bg-atelier-card border border-atelier-line rounded-2xl p-8 max-w-sm w-full text-center">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-clay mb-2">
            Outfit Atelier
          </p>
          <h1 className="font-display text-3xl text-ink mb-4">Style Checker</h1>
          <p className="text-ink/50 text-sm mb-5">
            What should we call you?
          </p>
          <input
            value={nameInput}
            onChange={(e) => setNameInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && createProfile()}
            placeholder="Your name"
            className="w-full bg-atelier-panel border border-atelier-line rounded-lg px-3 py-2 text-sm text-ink placeholder:text-ink/30 mb-3 focus:outline-none focus:ring-2 focus:ring-clay"
          />
          <button
            onClick={createProfile}
            className="w-full rounded-full bg-clay text-atelier-bg font-semibold py-2.5 hover:brightness-110 transition"
          >
            Start
          </button>
          {error && <p className="text-clay text-xs mt-3">{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen text-ink font-body">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <header className="mb-10">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-clay mb-2">
            Outfit Atelier
          </p>
          <h1 className="font-display text-4xl text-ink">Style Checker</h1>
          <p className="text-ink/50 mt-2 font-body">
            An on-demand color-coordination check, plus style tips based on the goal you pick —
            never a judgment of your body.
          </p>
        </header>

        {error && (
          <div className="mb-6 bg-clay/10 border border-clay/40 text-clay rounded-xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
          <WebcamPanel onCapture={handleCapture} busy={busy} />
          {prefs && <GoalPicker prefs={prefs} onChange={updatePrefs} />}
        </div>

        {result && (
          <div className="mb-5">
            <ResultCard result={result} />
          </div>
        )}

        <History items={history} />

        <footer className="mt-10 text-center text-ink/30 text-xs font-mono">
          Capture happens only when you click "Check my outfit" — nothing runs automatically.
        </footer>
      </div>
    </div>
  );
}
