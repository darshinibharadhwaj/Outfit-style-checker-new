import { useEffect, useState } from "react";
import {
  api,
  AuthError,
  tokenStore,
  type AnalyzeResult,
  type HistoryItem,
  type Preferences,
  type User
} from "./api";
import AuthPanel from "./components/AuthPanel";
import GoalPicker from "./components/GoalPicker";
import History from "./components/History";
import ResultCard from "./components/ResultCard";
import WebcamPanel, { BOTTOM_BOX, TOP_BOX } from "./components/WebcamPanel";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingLogin, setCheckingLogin] = useState(true);
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const logout = () => {
    tokenStore.clear();
    setUser(null);
    setPrefs(null);
    setResult(null);
    setHistory([]);
  };

  const handleError = (err: unknown, fallback: string) => {
    if (err instanceof AuthError) {
      logout();
      return;
    }
    setError(err instanceof Error ? err.message : fallback);
  };

  // On page load: if a saved login token exists, check it is still valid
  useEffect(() => {
    if (!tokenStore.get()) {
      setCheckingLogin(false);
      return;
    }
    api
      .me()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setCheckingLogin(false));
  }, []);

  useEffect(() => {
    if (!user) return;
    api.getPreferences().then(setPrefs).catch((e) => handleError(e, "Could not load your choices."));
    api.getHistory().then(setHistory).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const updatePrefs = async (next: Preferences) => {
    setPrefs(next);
    try {
      await api.updatePreferences(next);
    } catch (e) {
      handleError(e, "Could not save your choices.");
    }
  };

  const handleCapture = async (imageBase64: string) => {
    setBusy(true);
    setError(null);
    try {
      const res = await api.analyze({
        image_base64: imageBase64,
        top_box: TOP_BOX,
        bottom_box: BOTTOM_BOX
      });
      setResult(res);
      setHistory(await api.getHistory());
    } catch (e) {
      handleError(e, "Something went wrong checking the photo.");
    } finally {
      setBusy(false);
    }
  };

  if (checkingLogin) {
    return (
      <div className="min-h-screen flex items-center justify-center text-ink/50 font-body">
        Loading...
      </div>
    );
  }

  if (!user) {
    return <AuthPanel onLoggedIn={setUser} />;
  }

  return (
    <div className="min-h-screen text-ink font-body">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <header className="mb-10 flex items-start justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.3em] text-clay mb-2">
              Outfit Atelier
            </p>
            <h1 className="font-display text-4xl text-ink">Hello, {user.display_name}</h1>
            <p className="text-ink/50 mt-2 font-body">
              Check if your top and bottom match, and get simple tips for colours, accessories and
              shoes.
            </p>
          </div>
          <button
            onClick={logout}
            className="shrink-0 rounded-full border border-atelier-line text-ink/60 text-sm px-4 py-1.5 hover:border-ink/40 transition"
          >
            Log out
          </button>
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
          Your photo is checked only when you press "Check my outfit" and is never saved. Only the
          colours are kept.
        </footer>
      </div>
    </div>
  );
}
