#!/usr/bin/env python3
"""Overlay a huge number / title and a yellow subtitle on a 1280x720 thumbnail.

Fonts: set FONT_DIR to a folder that contains Anton-Regular.ttf (or pass --font).
Falls back to common system paths, including a local fonts/ directory.

Examples:
  python3 scripts/make_thumbnail.py --scene scene.jpg --out thumb.png \\
      --number "TOO HOT?" --subtitle "IT NEVER COOLED OFF" --anchor top

  python3 scripts/make_thumbnail.py --sheet thumb_a.png thumb_b.png --out preview.png
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
SMALL = (246, 138)  # YouTube suggested preview size


def font_candidates(name: str) -> list[Path]:
    env = os.environ.get("FONT_DIR")
    roots = []
    if env:
        roots.append(Path(env))
    here = Path(__file__).resolve().parent
    roots += [
        here / "fonts",
        here.parent / "fonts",
        Path("/usr/share/fonts/truetype/sand-box/google"),
        Path("/usr/share/fonts/truetype"),
        Path("/usr/share/fonts"),
        Path.home() / ".fonts",
        Path.home() / ".local/share/fonts",
    ]
    files = [
        name,
        f"{name}.ttf",
        f"{name}-Regular.ttf",
        f"Anton/{name}-Regular.ttf" if "Anton" in name or name == "Anton" else name,
    ]
    # Prefer an exact Anton file when the user asked for Anton.
    out = []
    for root in roots:
        if not root.is_dir():
            continue
        for fname in files:
            p = root / fname
            if p.is_file():
                out.append(p)
        # recursive basename search, shallow enough for font packs
        stem = Path(name).stem.replace("-Regular", "")
        for p in root.rglob("*.ttf"):
            if stem.lower() in p.stem.lower():
                out.append(p)
    # unique, keep order
    seen = set()
    uniq = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for path in font_candidates(name):
        try:
            return ImageFont.truetype(str(path), size)
        except OSError:
            continue
    raise SystemExit(
        f"Could not find font '{name}'. Install it or set FONT_DIR to a folder "
        f"that contains {name}-Regular.ttf (Anton is the default)."
    )


def overlay(
    scene: Path,
    out: Path,
    number: str,
    subtitle: str,
    anchor: str = "top",
    numsize: int = 200,
    subsize: int = 74,
    alpha: int = 120,
    font_name: str = "Anton",
) -> Path:
    im = Image.open(scene).convert("RGB").resize((W, H), Image.LANCZOS)
    fn, fs = load_font(font_name, numsize), load_font(font_name, subsize)
    d = ImageDraw.Draw(im)
    nb = d.textbbox((0, 0), number, font=fn, stroke_width=12)
    sb = d.textbbox((0, 0), subtitle, font=fs, stroke_width=7)
    nw, nh = nb[2] - nb[0], nb[3] - nb[1]
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    x = 36
    if anchor == "top":
        y = 18
    else:
        y = H - 28 - sh - 6 - nh
    sy = y + nh + 6
    bw = max(nw, sw) + 80
    bh = nh + sh + 60
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([x - 40, y - 20, x - 40 + bw, y - 20 + bh], 60, fill=alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(45))
    im = Image.composite(Image.new("RGB", (W, H), (5, 8, 15)), im, mask)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x - nb[0] + 10, y - nb[1] + 12), number, font=fn, fill=(0, 0, 0, 200), stroke_width=12, stroke_fill=(0, 0, 0, 200))
    sd.text((x - sb[0] + 6, sy - sb[1] + 7), subtitle, font=fs, fill=(0, 0, 0, 200), stroke_width=7, stroke_fill=(0, 0, 0, 200))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    im = Image.alpha_composite(im.convert("RGBA"), shadow)
    d = ImageDraw.Draw(im)
    d.text((x - nb[0], y - nb[1]), number, font=fn, fill=(255, 255, 255), stroke_width=12, stroke_fill=(12, 12, 18))
    d.text((x - sb[0], sy - sb[1]), subtitle, font=fs, fill=(255, 214, 0), stroke_width=7, stroke_fill=(12, 12, 18))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(out, optimize=True)
    print(f"wrote {out} ({W}x{H})")
    return out


def contact_sheet(paths: list[Path], out: Path, small: bool = False) -> Path:
    ims = [Image.open(p).convert("RGB") for p in paths]
    if small:
        tw, th = SMALL
        pad = 10
        sheet = Image.new("RGB", (tw * len(ims) + pad * (len(ims) + 1), th + pad * 2), (24, 24, 28))
        for i, im in enumerate(ims):
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (pad + i * (tw + pad), pad))
    else:
        tw, th = 640, 360
        pad = 20
        sheet = Image.new("RGB", (tw * len(ims) + pad * (len(ims) + 1), th + pad * 2 + 40), (24, 24, 28))
        sd = ImageDraw.Draw(sheet)
        try:
            lf = load_font("Anton", 26)
        except SystemExit:
            lf = ImageFont.load_default()
        for i, (im, name) in enumerate(zip(ims, paths)):
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (pad + i * (tw + pad), pad))
            sd.text((pad + i * (tw + pad), pad + th + 8), name.name, font=lf, fill=(220, 220, 220))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"wrote {out}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", type=Path, help="Background image (cropped/resized to 1280x720)")
    ap.add_argument("--out", type=Path, required=True, help="Output PNG or JPG")
    ap.add_argument("--number", default="", help='Huge top line, e.g. "30 DAYS" or "TOO HOT?"')
    ap.add_argument("--subtitle", default="", help="Yellow subtitle under the number")
    ap.add_argument("--anchor", choices=["top", "bottom"], default="top")
    ap.add_argument("--numsize", type=int, default=200)
    ap.add_argument("--subsize", type=int, default=74)
    ap.add_argument("--alpha", type=int, default=120, help="Dark backing strength, 0–255")
    ap.add_argument("--font", default="Anton", help="Font family name or file stem")
    ap.add_argument("--sheet", nargs="+", type=Path, help="Build a contact sheet from existing thumbs instead")
    ap.add_argument("--small", action="store_true", help="With --sheet, use 246x138 cells")
    args = ap.parse_args()

    if args.sheet:
        contact_sheet(args.sheet, args.out, small=args.small)
        return 0
    if not args.scene:
        ap.error("--scene is required unless you pass --sheet")
    overlay(
        args.scene,
        args.out,
        args.number,
        args.subtitle,
        anchor=args.anchor,
        numsize=args.numsize,
        subsize=args.subsize,
        alpha=args.alpha,
        font_name=args.font,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
