#!/usr/bin/env python3
"""Optional F5-TTS generation.

F5-TTS is licensed for NON-COMMERCIAL use. Do not use this script on a
monetized channel. This repo does not include any voice-clone reference
audio — you must pass your own --ref and --ref-text if you use it at all.

Prefer scripts/voices/edge_tts_gen.py or chatterbox_gen.py for published work.

Example:
  python3 scripts/voices/f5_gen.py \\
      --ref /path/to/your_ref.wav --ref-text "A transcript of that clip." \\
      --text "Something just hit the floor upstairs." --out line.wav
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", type=Path, required=True, help="Your reference wav (not included in this repo)")
    ap.add_argument("--ref-text", required=True, help="Transcript of the reference audio")
    ap.add_argument("--text", required=True, help="Text to generate")
    ap.add_argument("--out", type=Path, default=Path("out.wav"))
    ap.add_argument("--speed", type=float, default=0.9)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    if not args.ref.is_file():
        raise SystemExit(f"Reference audio not found: {args.ref}")

    import torch
    from f5_tts.api import F5TTS

    torch.set_num_threads(8)
    model = F5TTS(model="F5TTS_v1_Base", device=args.device)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    model.infer(
        ref_file=str(args.ref),
        ref_text=args.ref_text,
        gen_text=args.text,
        file_wave=str(args.out),
        seed=args.seed,
        speed=args.speed,
    )
    print(args.out, "gen", round(time.time() - t0, 1), "s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
