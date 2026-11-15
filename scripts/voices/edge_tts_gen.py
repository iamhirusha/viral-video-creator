#!/usr/bin/env python3
"""Generate speech with Microsoft Edge neural voices (free, needs network).

Examples:
  python3 scripts/voices/edge_tts_gen.py --list
  python3 scripts/voices/edge_tts_gen.py --voice en-US-AvaMultilingualNeural \\
      --text "Something just hit the floor upstairs." --out narrator.mp3 --rate -8%
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import edge_tts


async def list_voices(filter_lang: str | None) -> None:
    voices = await edge_tts.list_voices()
    for v in voices:
        loc = v.get("Locale") or ""
        if filter_lang and filter_lang.lower() not in loc.lower() and filter_lang.lower() not in v.get("ShortName", "").lower():
            continue
        print(f"{v['ShortName']:40s}  {loc:12s}  {v.get('Gender', ''):8s}  {v.get('FriendlyName', '')}")


async def synth(text: str, voice: str, out: Path, rate: str, pitch: str) -> None:
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    out.parent.mkdir(parents=True, exist_ok=True)
    await communicate.save(str(out))
    print(f"wrote {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="List available voices")
    ap.add_argument("--lang", default="en", help="When listing, filter by locale or short name (default: en)")
    ap.add_argument("--voice", default="en-US-AvaMultilingualNeural")
    ap.add_argument("--text", default="", help="Text to speak")
    ap.add_argument("--text-file", type=Path, help="Read text from a file instead")
    ap.add_argument("--out", type=Path, default=Path("out.mp3"))
    ap.add_argument("--rate", default="+0%", help='Edge rate, e.g. "-10%" or "+5%"')
    ap.add_argument("--pitch", default="+0Hz", help='Edge pitch, e.g. "-40Hz"')
    args = ap.parse_args()

    if args.list:
        asyncio.run(list_voices(args.lang))
        return 0
    text = args.text or (args.text_file.read_text(encoding="utf-8") if args.text_file else "")
    if not text.strip():
        ap.error("pass --text or --text-file")
    asyncio.run(synth(text.strip(), args.voice, args.out, args.rate, args.pitch))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
