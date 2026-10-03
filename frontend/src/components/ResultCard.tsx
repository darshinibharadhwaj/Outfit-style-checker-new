import type { AnalyzeResult } from "../api";

const VERDICT_STYLE: Record<AnalyzeResult["verdict"], { label: string; cls: string }> = {
  good: { label: "Looks good", cls: "bg-sage/20 text-sage border-sage/50" },
  ok: { label: "Okay", cls: "bg-gold/15 text-gold border-gold/50" },
  change: { label: "Try a change", cls: "bg-clay/15 text-clay border-clay/50" }
};

function Section({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="mb-5">
      <p className="text-[10px] uppercase tracking-widest text-ink/40 mb-2 font-mono">{title}</p>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-ink/80 font-body leading-snug">
            • {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ResultCard({ result }: { result: AnalyzeResult }) {
  const scorePercent = Math.round(result.harmony_score * 100);
  const verdict = VERDICT_STYLE[result.verdict];

  return (
    <div className="bg-atelier-card border border-atelier-line rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <p className="font-display text-xl text-ink">Your result</p>
        <span className={`text-xs font-medium border rounded-full px-3 py-1 ${verdict.cls}`}>
          {verdict.label}
        </span>
      </div>

      <div className="flex items-center gap-6 mb-5">
        <div className="flex flex-col items-center gap-1">
          <div className="swatch-chip">
            <div className="w-16 h-16 rounded" style={{ backgroundColor: result.top_color }} />
          </div>
          <span className="text-sm text-ink capitalize">{result.top_name}</span>
          <span className="text-[10px] uppercase tracking-widest text-gold">Top</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="swatch-chip">
            <div className="w-16 h-16 rounded" style={{ backgroundColor: result.bottom_color }} />
          </div>
          <span className="text-sm text-ink capitalize">{result.bottom_name}</span>
          <span className="text-[10px] uppercase tracking-widest text-sage">Bottom</span>
        </div>
      </div>

      <p className="font-display text-lg text-ink mb-1">{result.summary}</p>
      <div className="w-full h-2 bg-atelier-panel rounded-full overflow-hidden mb-2">
        <div
          className="h-full bg-clay transition-all duration-500"
          style={{ width: `${scorePercent}%` }}
        />
      </div>
      <p className="text-ink/60 text-sm font-body mb-5">
        {result.harmony_label}. {result.detail}
      </p>

      <Section title="Is this colour good for your skin tone?" items={result.skin_advice} />
      <Section title="Other colours that go with it" items={result.alternatives} />
      <Section title="Accessories" items={result.accessories} />
      <Section title="Shoes" items={result.footwear} />
      <Section title="Style tips for your goal" items={result.tips} />
    </div>
  );
}
