import type { Preferences } from "../api";

const GOALS: { value: string; label: string; hint: string }[] = [
  { value: "structure", label: "Add structure", hint: "sharper, more tailored" },
  { value: "balance", label: "Balance proportions", hint: "even top-to-bottom" },
  { value: "elongate", label: "Elongate", hint: "lengthen the silhouette" },
  { value: "relaxed", label: "Relaxed & easy", hint: "comfortable, low-effort" }
];

const OCCASIONS = ["casual", "office", "formal", "evening"];

interface Props {
  prefs: Preferences;
  onChange: (prefs: Preferences) => void;
}

export default function GoalPicker({ prefs, onChange }: Props) {
  return (
    <div className="bg-atelier-card border border-atelier-line rounded-2xl p-5">
      <p className="font-display text-xl text-ink mb-1">Your style goal</p>
      <p className="text-ink/50 text-sm font-body mb-4">
        You choose this yourself — tips are matched to what you pick, not to any
        analysis of your body.
      </p>

      <div className="grid grid-cols-2 gap-2 mb-4">
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

      <label className="block text-[10px] uppercase tracking-widest text-ink/40 font-mono mb-1">
        Usual occasion
      </label>
      <select
        value={prefs.preferred_occasion}
        onChange={(e) => onChange({ ...prefs, preferred_occasion: e.target.value })}
        className="w-full bg-atelier-panel border border-atelier-line rounded-lg px-3 py-2 text-sm text-ink font-body focus:outline-none focus:ring-2 focus:ring-clay"
      >
        {OCCASIONS.map((o) => (
          <option key={o} value={o}>
            {o[0].toUpperCase() + o.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
}
