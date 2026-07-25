import type { HistoryItem } from "../api";

function formatTime(dateStr: string) {
  const d = new Date(dateStr + "Z");
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

export default function History({ items }: { items: HistoryItem[] }) {
  return (
    <div className="bg-atelier-card border border-atelier-line rounded-2xl p-5">
      <p className="font-display text-xl text-ink mb-3">Past checks</p>
      {items.length === 0 ? (
        <p className="text-ink/40 text-sm font-body">No checks yet — try one above.</p>
      ) : (
        <ul className="divide-y divide-atelier-line">
          {items.map((item) => (
            <li key={item.id} className="py-3 flex items-center gap-3">
              <div className="flex gap-1">
                <div
                  className="w-6 h-6 rounded"
                  style={{ backgroundColor: item.top_color_hex }}
                />
                <div
                  className="w-6 h-6 rounded"
                  style={{ backgroundColor: item.bottom_color_hex }}
                />
              </div>
              <div className="flex-1">
                <p className="text-sm text-ink/80 font-body">{item.harmony_label}</p>
              </div>
              <span className="font-mono text-xs text-ink/40">
                {formatTime(item.created_at)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
