import { useState } from "react";
import { api, tokenStore, type User } from "../api";

interface Props {
  onLoggedIn: (user: User) => void;
}

export default function AuthPanel({ onLoggedIn }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setError(null);
    if (!username.trim() || !password) {
      setError("Please enter your username and password.");
      return;
    }
    if (mode === "register") {
      if (!displayName.trim()) return setError("Please enter your name.");
      if (!/^[A-Za-z0-9_]{3,30}$/.test(username.trim()))
        return setError("Username: 3 to 30 letters, numbers or underscore (no spaces).");
      if (password.length < 6) return setError("Password must be at least 6 characters.");
    }
    setBusy(true);
    try {
      const res =
        mode === "login"
          ? await api.login(username.trim(), password)
          : await api.register(username.trim(), password, displayName.trim());
      tokenStore.set(res.access_token);
      onLoggedIn(res.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reach the server.");
    } finally {
      setBusy(false);
    }
  };

  const input =
    "w-full bg-atelier-panel border border-atelier-line rounded-lg px-3 py-2.5 text-sm text-ink placeholder:text-ink/30 mb-3 focus:outline-none focus:ring-2 focus:ring-clay";

  return (
    <div className="min-h-screen flex items-center justify-center text-ink font-body px-6">
      <div className="bg-atelier-card border border-atelier-line rounded-2xl p-8 max-w-sm w-full">
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-clay mb-2 text-center">
          Outfit Atelier
        </p>
        <h1 className="font-display text-3xl text-ink mb-1 text-center">Style Checker</h1>
        <p className="text-ink/50 text-sm mb-6 text-center">
          Check if your clothes match, in simple words. No fashion knowledge needed.
        </p>

        <div className="grid grid-cols-2 gap-2 mb-5">
          {(["login", "register"] as const).map((m) => (
            <button
              key={m}
              onClick={() => {
                setMode(m);
                setError(null);
              }}
              className={`rounded-full py-2 text-sm font-medium border transition-colors ${
                mode === m
                  ? "border-clay bg-clay/10 text-ink"
                  : "border-atelier-line text-ink/50 hover:border-ink/30"
              }`}
            >
              {m === "login" ? "Log in" : "Create account"}
            </button>
          ))}
        </div>

        {mode === "register" && (
          <input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Your name"
            autoComplete="name"
            className={input}
          />
        )}
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          autoComplete="username"
          autoCapitalize="none"
          className={input}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Password (at least 6 characters)"
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          className={input}
        />

        <button
          onClick={submit}
          disabled={busy}
          className="w-full rounded-full bg-clay text-atelier-bg font-semibold py-2.5 hover:brightness-110 transition disabled:opacity-50"
        >
          {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
        </button>
        {error && <p className="text-clay text-sm mt-3 text-center">{error}</p>}
      </div>
    </div>
  );
}
