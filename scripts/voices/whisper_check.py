#!/usr/bin/env python3
"""Transcribe a voice take with faster-whisper and optionally score WER / pitch.

Examples:
  python3 scripts/voices/whisper_check.py take.wav
  python3 scripts/voices/whisper_check.py take.wav --expect "Something just hit the floor upstairs."
  python3 scripts/voices/whisper_check.py samples/*.mp3 --expect-file lines.txt
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def norm(s: str) -> list[str]:
    return re.sub(r"[^a-z ]", "", s.lower()).split()


def wer(ref: list[str], hyp: list[str]) -> float:
    if not ref:
        return 0.0 if not hyp else 1.0
    d = np.arange(len(hyp) + 1)
    for i, rw in enumerate(ref, 1):
        prev, d[0] = d.copy(), i
        for j, hw in enumerate(hyp, 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (rw != hw))
    return float(d[-1] / len(ref))


def load_audio(path: Path, sr: int = 16000) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.float32)


def f0_stats(a: np.ndarray, sr: int = 16000):
    fr, hop = 640, 160
    f0 = []
    for i in range(0, len(a) - fr, hop):
        x = a[i : i + fr]
        if np.sqrt((x ** 2).mean()) < 0.01:
            continue
        c = np.correlate(x, x, "full")[fr - 1 :]
        lo, hi = sr // 500, sr // 70
        k = lo + int(np.argmax(c[lo:hi]))
        if c[k] / c[0] > 0.45:
            f0.append(sr / k)
    f0 = np.array(f0)
    if len(f0) == 0:
        return 0.0, 0.0, 0.0
    var = float(np.std(12 * np.log2(f0 / np.median(f0)))) if len(f0) > 5 else 0.0
    voiced = len(f0) / max(1, (len(a) - fr) // hop)
    return float(np.median(f0)), var, voiced


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path, help="Audio files to check")
    ap.add_argument("--expect", default="", help="Expected transcript for WER (applied to every file)")
    ap.add_argument("--expect-file", type=Path, help="File with one expected line, or name<TAB>line per row")
    ap.add_argument("--model", default="small.en", help="faster-whisper model (default: small.en)")
    args = ap.parse_args()

    expected_map = {}
    default_expect = args.expect
    if args.expect_file:
        for ln in args.expect_file.read_text(encoding="utf-8").splitlines():
            if not ln.strip() or ln.startswith("#"):
                continue
            if "\t" in ln:
                name, text = ln.split("\t", 1)
                expected_map[name.strip()] = text.strip()
            else:
                default_expect = default_expect or ln.strip()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    for path in args.files:
        a = load_audio(path)
        segs, _ = model.transcribe(a, language="en", beam_size=5)
        segs = list(segs)
        txt = " ".join(s.text.strip() for s in segs)
        lp = float(np.mean([s.avg_logprob for s in segs])) if segs else -9.0
        med, semis, voiced = f0_stats(a)
        expect = expected_map.get(path.name) or expected_map.get(path.stem) or default_expect
        wer_s = f"WER {wer(norm(expect), norm(txt)):.2f} " if expect else ""
        print(
            f"{path.name:28s} dur {len(a)/16000:4.1f}s {wer_s}"
            f"f0 {med:4.0f}Hz var {semis:3.1f}st voiced {voiced:.2f} "
            f"peak {np.abs(a).max():.2f} lp {lp:.2f} | {txt}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
