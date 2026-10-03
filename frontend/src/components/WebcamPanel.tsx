import { useEffect, useRef, useState } from "react";

// Fixed guide regions as fractions of the frame (left, top, right, bottom).
// The user aligns their shirt/trousers inside these guides before capturing.
export const TOP_BOX: [number, number, number, number] = [0.28, 0.16, 0.72, 0.42];
export const BOTTOM_BOX: [number, number, number, number] = [0.28, 0.52, 0.72, 0.85];

const MAX_WIDTH = 640; // shrink the photo before sending so it uploads fast on slow mobile data

interface Props {
  onCapture: (imageBase64: string) => void;
  busy: boolean;
}

export default function WebcamPanel({ onCapture, busy }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [facing, setFacing] = useState<"user" | "environment">("user");

  useEffect(() => {
    let stream: MediaStream | null = null;
    let cancelled = false;
    setReady(false);

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: facing } });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setReady(true);
          setError(null);
        }
      } catch {
        setError(
          "Couldn't open your camera. Please allow camera permission for this website, and use a secure (https) link."
        );
      }
    }
    start();

    return () => {
      cancelled = true;
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, [facing]);

  const capture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !video.videoWidth) return;

    const scale = Math.min(1, MAX_WIDTH / video.videoWidth);
    canvas.width = Math.round(video.videoWidth * scale);
    canvas.height = Math.round(video.videoHeight * scale);
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    onCapture(canvas.toDataURL("image/jpeg", 0.85));
  };

  return (
    <div className="bg-atelier-card border border-atelier-line rounded-2xl p-5">
      <p className="font-display text-xl text-ink mb-1">Check your outfit</p>
      <p className="text-ink/50 text-sm font-body mb-4">
        Stand back so your top and bottom fit inside the two dashed boxes (a friend can hold the phone
        with the back camera). Then press the button. Nothing is captured until you press it.
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

      <div className="mt-4 flex gap-2">
        <button
          onClick={capture}
          disabled={!ready || busy}
          className="flex-1 rounded-full bg-clay text-atelier-bg font-body font-semibold py-2.5 disabled:opacity-40 hover:brightness-110 transition"
        >
          {busy ? "Checking..." : "Check my outfit"}
        </button>
        <button
          onClick={() => setFacing((f) => (f === "user" ? "environment" : "user"))}
          disabled={busy}
          className="rounded-full border border-atelier-line text-ink/70 text-sm px-4 hover:border-ink/40 transition disabled:opacity-40"
        >
          Switch camera
        </button>
      </div>
    </div>
  );
}
