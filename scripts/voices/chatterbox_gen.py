#!/usr/bin/env python3
"""Generate speech with Chatterbox TTS (MIT licence, local).

Do not ship or commit other people's voices. If you pass --ref, use audio you
have the rights to, or omit it to use the model's default voice.

Examples:
  python3 scripts/voices/chatterbox_gen.py --text "Something just hit the floor upstairs." --out narrator.wav
  python3 scripts/voices/chatterbox_gen.py --jobs jobs.example.txt --outdir ./out

Jobs file format (one per line, | separated):
  name|DEFAULT_or_path_to_ref.wav|exaggeration|cfg_weight|temperature|text
"""
from __future__ import annotations

import argparse
import copy
import sys
import time
from pathlib import Path


def generate_one(model, default_conds, name, ref, exaggeration, cfg, temp, text, outdir: Path):
    import torch
    import torchaudio as ta

    torch.manual_seed(42)
    t0 = time.time()
    if not ref or ref.upper() == "DEFAULT":
        model.conds = copy.deepcopy(default_conds)
        ref_path = None
    else:
        ref_path = ref
        if not Path(ref_path).is_file():
            raise FileNotFoundError(f"Reference audio not found: {ref_path}")
    wav = model.generate(
        text,
        audio_prompt_path=ref_path,
        exaggeration=float(exaggeration),
        cfg_weight=float(cfg),
        temperature=float(temp),
    )
    out = outdir / f"{name}.wav"
    outdir.mkdir(parents=True, exist_ok=True)
    ta.save(str(out), wav, model.sr)
    print(name, "gen", round(time.time() - t0, 1), "s  audio", round(wav.shape[-1] / model.sr, 2), "s", "->", out, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", default="")
    ap.add_argument("--out", type=Path, default=Path("out.wav"))
    ap.add_argument("--ref", default="DEFAULT", help="DEFAULT, or a path to reference audio you have rights to")
    ap.add_argument("--exaggeration", type=float, default=0.5)
    ap.add_argument("--cfg", type=float, default=0.3)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--jobs", type=Path, help="Batch file; see jobs.example.txt")
    ap.add_argument("--outdir", type=Path, default=Path("."))
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    import torch
    from chatterbox.tts import ChatterboxTTS

    torch.set_num_threads(8)
    model = ChatterboxTTS.from_pretrained(device=args.device)
    default_conds = copy.deepcopy(model.conds)

    if args.jobs:
        lines = [ln for ln in args.jobs.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]
        for ln in lines:
            parts = ln.split("|")
            if len(parts) != 6:
                raise SystemExit(f"Bad jobs line (want 6 |-fields): {ln}")
            name, ref, ex, cfg, temp, text = parts
            generate_one(model, default_conds, name, ref, ex, cfg, temp, text, args.outdir)
        return 0

    if not args.text.strip():
        ap.error("pass --text or --jobs")
    generate_one(
        model,
        default_conds,
        args.out.stem,
        args.ref,
        args.exaggeration,
        args.cfg,
        args.temp,
        args.text,
        args.out.parent,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
