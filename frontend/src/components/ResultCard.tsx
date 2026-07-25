import type { AnalyzeResult } from "../api";

interface Props {
  result: AnalyzeResult;
}

export default function ResultCard({ result }: Props) {
  const scorePercent = Math.round(result.harmony_score * 100);

  return (
    <div className="bg-atelier-card border border-atelier-line rounded-2xl p-5">
      <p className="font-display text-xl text-ink mb-4">Result</p>

      <div className="flex items-center gap-6 mb-5">
        <div className="flex flex-col items-center gap-2">
          <div className="swatch-chip">
            <div
              className="w-16 h-16 rounded"
              style={{ backgroundColor: result.top_color }}
            />
          </div>
          <span className="font-mono text-xs text-ink/60">{result.top_color}</span>
          <span className="text-[10px] uppercase tracking-widest text-gold">Top</span>
        </div>
        <div className="flex flex-col items-center gap-2">
          <div className="swatch-chip">
            <div
              className="w-16 h-16 rounded"
              style={{ backgroundColor: result.bottom_color }}
            />
          </div>
          <span className="font-mono text-xs text-ink/60">{result.bottom_color}</span>
          <span className="text-[10px] uppercase tracking-widest text-sage">Bottom</span>
        </div>
      </div>

      <p className="font-display text-lg text-ink mb-1">{result.harmony_label}</p>
      <div className="w-full h-2 bg-atelier-panel rounded-full overflow-hidden mb-2">
        <div
          className="h-full bg-clay transition-all duration-500"
          style={{ width: `${scorePercent}%` }}
        />
      </div>
      <p className="text-ink/60 text-sm font-body mb-4">{result.detail}</p>

      {result.tips.length > 0 && (
        <div>
          <p className="text-[10px] uppercase tracking-widest text-ink/40 mb-2 font-mono">
            Style tips for your goal
          </p>
          <ul className="space-y-2">
            {result.tips.map((tip, i) => (
              <li key={i} className="text-sm text-ink/80 font-body leading-snug">
                • {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
