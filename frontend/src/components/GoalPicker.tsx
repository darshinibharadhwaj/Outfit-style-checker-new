import type { Preferences } from "../api";

const GOALS: { value: string; label: string; hint: string }[] = [
  { value: "structure", label: "Add structure", hint: "sharper, more tailored" },
  { value: "balance", label: "Balance proportions", hint: "even top-to-bottom" },
  { value: "elongate", label: "Elongate", hint: "lengthen the silhouette" },
  { value: "relaxed", label: "Relaxed & easy", hint: "comfortable, low-effort" }
];

const OCCASIONS: { value: string; label: string }[] = [
  { value: "casual", label: "Casual (daily)" },
  { value: "office", label: "Office / college" },
  { value: "formal", label: "Formal" },
  { value: "evening", label: "Evening / party" },
  { value: "festival", label: "Festival / function" }
];

// Swatches are only a visual guide to help you pick; you choose, nothing is detected.
const SKIN_TONES: { value: string; label: string; swatch: string }[] = [
  { value: "fair", label: "Fair", swatch: "#F1D3BC" },
  { value: "wheatish", label: "Wheatish", swatch: "#D9A67E" },
  { value: "medium", label: "Medium brown", swatch: "#B67B52" },
  { value: "dusky", label: "Dusky", swatch: "#8A5A3C" },
  { value: "deep", label: "Deep", swatch: "#5B3A29" }
];

interface Props {
  prefs: Preferences;
  onChange: (prefs: Preferences) => void;
}

export default function GoalPicker({ prefs, onChange }: Props) {
  const label =
    "block text-[10px] uppercase tracking-widest text-ink/40 font-mono mb-1";

  return (
    <div className="bg-atelier-card border border-atelier-line rounded-2xl p-5">
      <p className="font-display text-xl text-ink mb-1">About you</p>
      <p className="text-ink/50 text-sm font-body mb-4">
        You choose these yourself. Suggestions follow your choices; nothing is guessed from your face
        or body.
      </p>

      <span className={label}>Your skin tone</span>
      <div className="flex gap-2 mb-4 flex-wrap">
        {SKIN_TONES.map((t) => (
          <button
            key={t.value}
            onClick={() => onChange({ ...prefs, skin_tone: t.value })}
            className={`flex items-center gap-2 rounded-full border px-3 py-1.5 transition-colors ${
              prefs.skin_tone === t.value
                ? "border-clay bg-clay/10 text-ink"
                : "border-atelier-line text-ink/60 hover:border-ink/30"
            }`}
          >
            <span className="w-4 h-4 rounded-full" style={{ backgroundColor: t.swatch }} />
            <span className="text-xs font-body">{t.label}</span>
          </button>
        ))}
      </div>

      <span className={label}>Where are you going?</span>
      <select
        value={prefs.preferred_occasion}
        onChange={(e) => onChange({ ...prefs, preferred_occasion: e.target.value })}
        className="w-full bg-atelier-panel border border-atelier-line rounded-lg px-3 py-2 text-sm text-ink font-body mb-4 focus:outline-none focus:ring-2 focus:ring-clay"
      >
        {OCCASIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>

      <span className={label}>Your style goal</span>
      <div className="grid grid-cols-2 gap-2">
        {GOALS.map((g) => (
          <button
            key={g.value}
            onClick={() => onChange({ ...prefs, style_goal: g.value })}
            className={`text-left rounded-xl border px-3 py-2 transition-colors ${
              prefs.style_goal === g.value
                ? "border-clay bg-clay/10 text-ink"
                : "border-atelier-line text-ink/60 hover:border-ink/30"
            }`}
          >
            <p className="text-sm font-body font-medium">{g.label}</p>
            <p className="text-[11px] text-ink/40">{g.hint}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
