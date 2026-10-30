"""Transcribe the teacher's voice notes with word timestamps (for per-phrase clips).

    python3 scripts/transcribe.py            # all notes referenced in data/days/*.json
Writes data/transcripts/<note>.json and skips notes already done. Runs ~real time on 2 CPU cores.
"""
import glob, json, os, re, subprocess, sys, time
import numpy as np
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "docs", "audio")
OUT = os.path.join(ROOT, "data", "transcripts")


def jobs():
    j = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "days", "day*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        for b in d["blocks"]:
            ph = []
            for s in b["sections"]:
                for it in s["items"]:
                    a = re.sub(r"\[[rbg]:([^\]]+)\]", lambda m: m.group(1).split("|")[0], it["ar"])
                    ph.append(re.sub(r"[\u064B-\u0652\u0670]", "", a))
            for f in b.get("intro", []) + b.get("audio", []):
                j[f] = "، ".join(ph)[:600]   # lesson phrases as a hint to the recogniser
    return j


def main():
    os.makedirs(OUT, exist_ok=True)
    model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 2)
    for f, prompt in jobs().items():
        o = os.path.join(OUT, f + ".json")
        if os.path.exists(o):
            continue
        t = time.time()
        raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", os.path.join(AUDIO, f),
                              "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
        segs, _ = model.transcribe(np.frombuffer(raw, np.float32), language="ar", beam_size=1, word_timestamps=True,
                                   vad_filter=True, vad_parameters={"min_silence_duration_ms": 700},
                                   initial_prompt=prompt, condition_on_previous_text=False)
        out = [{"s": s.start, "e": s.end, "t": s.text, "w": [[w.start, w.end, w.word] for w in s.words]} for s in segs]
        json.dump(out, open(o, "w", encoding="utf-8"), ensure_ascii=False)
        print(f, round(time.time() - t), "s", flush=True)
    print("done")


if __name__ == "__main__":
    main()
