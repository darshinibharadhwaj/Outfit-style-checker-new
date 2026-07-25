import { useEffect, useRef, useState } from "react";

// Fixed guide regions as fractions of the frame (left, top, right, bottom).
// The user aligns their shirt/trousers inside these guides before capturing.
export const TOP_BOX: [number, number, number, number] = [0.28, 0.16, 0.72, 0.42];
export const BOTTOM_BOX: [number, number, number, number] = [0.28, 0.52, 0.72, 0.85];

interface Props {
  onCapture: (imageBase64: string) => void;
  busy: boolean;
}

export default function WebcamPanel({ onCapture, busy }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let stream: MediaStream | null = null;

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setReady(true);
        }
      } catch (err) {
        setError("Couldn't access your camera. Check your browser's camera permission for this site.");
      }
    }
    start();

    return () => {
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const capture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.85);
    onCapture(dataUrl);
  };

  return (
    <div className="bg-atelier-card border border-atelier-line rounded-2xl p-5">
      <p className="font-display text-xl text-ink mb-1">On-demand outfit check</p>
      <p className="text-ink/50 text-sm font-body mb-4">
        Align your top and bottom inside the two guide boxes, then click the button below.
        Nothing is captured until you choose to.
      </p>

      {error ? (
        <div className="bg-clay/10 border border-clay/40 text-clay rounded-lg px-4 py-3 text-sm">
          {error}
        </div>
      ) : (
        <div className="relative rounded-xl overflow-hidden bg-black aspect-[3/4] max-w-sm mx-auto">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
          {/* Guide overlays */}
          <div
            className="absolute border-2 border-dashed border-gold/80 rounded-md"
            style={{
              left: `${TOP_BOX[0] * 100}%`,
              top: `${TOP_BOX[1] * 100}%`,
              width: `${(TOP_BOX[2] - TOP_BOX[0]) * 100}%`,
              height: `${(TOP_BOX[3] - TOP_BOX[1]) * 100}%`
            }}
          >
            <span className="absolute -top-5 left-0 text-[10px] font-mono text-gold">TOP</span>
          </div>
          <div
            className="absolute border-2 border-dashed border-sage/80 rounded-md"
            style={{
              left: `${BOTTOM_BOX[0] * 100}%`,
              top: `${BOTTOM_BOX[1] * 100}%`,
              width: `${(BOTTOM_BOX[2] - BOTTOM_BOX[0]) * 100}%`,
              height: `${(BOTTOM_BOX[3] - BOTTOM_BOX[1]) * 100}%`
            }}
          >
            <span className="absolute -top-5 left-0 text-[10px] font-mono text-sage">BOTTOM</span>
          </div>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />

      <button
        onClick={capture}
        disabled={!ready || busy}
        className="mt-4 w-full rounded-full bg-clay text-atelier-bg font-body font-semibold py-2.5 disabled:opacity-40 hover:brightness-110 transition"
      >
        {busy ? "Analyzing..." : "Check my outfit"}
      </button>
    </div>
  );
}
