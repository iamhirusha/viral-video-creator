#!/usr/bin/env python3
"""Pull YouTube channel video lists with yt-dlp and print a teardown-style report.

Writes a CSV (channel, id, upload_date, views, likes, comments, duration_s,
title, views_per_sub). Does not copy titles into a script, and does not commit
other people's transcripts — --subs only writes to a local folder you choose.

Examples:
  python3 scripts/channel_research.py --out data/ https://www.youtube.com/@somechannel/videos
  python3 scripts/channel_research.py --csv data/videos.csv
  python3 scripts/channel_research.py --out data/ --subs 3 --subs-dir data/subs @somechannel
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


CSV_FIELDS = [
    "channel",
    "id",
    "upload_date",
    "views",
    "likes",
    "comments",
    "duration_s",
    "title",
    "views_per_sub",
]


def run_yt_dlp(args: list[str]) -> subprocess.CompletedProcess:
    cmd = ["yt-dlp", *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def as_channel_url(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("@"):
        raw = f"https://www.youtube.com/{raw}/videos"
    elif re.fullmatch(r"[\w.-]+", raw):
        raw = f"https://www.youtube.com/@{raw}/videos"
    elif "/videos" not in raw and "list=" not in raw:
        raw = raw.rstrip("/") + "/videos"
    return raw


def channel_slug(url: str) -> str:
    path = urlparse(url).path.strip("/")
    for part in path.split("/"):
        if part.startswith("@") or part not in {"videos", "shorts", "streams", "c", "channel", "user"}:
            return re.sub(r"[^A-Za-z0-9_@.-]", "_", part) or "channel"
    return "channel"


def load_entries(url: str) -> tuple[list[dict], dict]:
    proc = run_yt_dlp(["--flat-playlist", "-J", "--no-warnings", url])
    if proc.returncode != 0:
        raise SystemExit(f"yt-dlp failed for {url}:\n{proc.stderr or proc.stdout}")
    payload = json.loads(proc.stdout)
    entries = [e for e in (payload.get("entries") or []) if e and e.get("id")]
    meta = {
        "channel": payload.get("channel") or payload.get("uploader") or channel_slug(url),
        "channel_id": payload.get("channel_id") or payload.get("uploader_id"),
        "followers": payload.get("channel_follower_count") or payload.get("playlist_count"),
    }
    return entries, meta


def enrich(entries: list[dict], followers: int | None, full: bool) -> list[dict]:
    rows = []
    missing = []
    for e in entries:
        row = {
            "channel": e.get("channel") or e.get("uploader") or "",
            "id": e.get("id"),
            "upload_date": e.get("upload_date") or "",
            "views": e.get("view_count"),
            "likes": e.get("like_count"),
            "comments": e.get("comment_count"),
            "duration_s": e.get("duration"),
            "title": (e.get("title") or "").replace("\n", " ").strip(),
        }
        if row["views"] is None or (full and (not row["upload_date"] or row["duration_s"] is None)):
            missing.append(row)
        rows.append(row)

    if missing and (full or any(r["views"] is None for r in missing)):
        ids = [r["id"] for r in missing]
        # Batch metadata without downloading media.
        proc = run_yt_dlp(
            [
                "--skip-download",
                "--no-warnings",
                "-J",
                "--no-playlist",
                *[f"https://www.youtube.com/watch?v={i}" for i in ids],
            ]
        )
        if proc.returncode != 0 and not proc.stdout.strip():
            print(f"warning: could not enrich {len(ids)} videos:\n{proc.stderr}", file=sys.stderr)
        else:
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError:
                payload = None
            items = []
            if payload:
                items = payload.get("entries") or [payload]
            by_id = {it.get("id"): it for it in items if it}
            for row in missing:
                it = by_id.get(row["id"]) or {}
                row["channel"] = row["channel"] or it.get("channel") or it.get("uploader") or ""
                row["upload_date"] = row["upload_date"] or it.get("upload_date") or ""
                if row["views"] is None:
                    row["views"] = it.get("view_count")
                if row["likes"] is None:
                    row["likes"] = it.get("like_count")
                if row["comments"] is None:
                    row["comments"] = it.get("comment_count")
                if row["duration_s"] is None:
                    row["duration_s"] = it.get("duration")
                if not row["title"] or row["title"] in {"[Private video]", "[Deleted video]"}:
                    row["title"] = (it.get("title") or row["title"]).replace("\n", " ").strip()

    for row in rows:
        views = _num(row["views"])
        row["views"] = views
        row["likes"] = _num(row["likes"])
        row["comments"] = _num(row["comments"])
        row["duration_s"] = _num(row["duration_s"])
        row["views_per_sub"] = round(views / followers, 2) if views is not None and followers else ""
    return rows


def _num(v):
    if v in (None, "", "NA"):
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow({k: "" if row.get(k) is None else row.get(k) for k in CSV_FIELDS})


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for k in ("views", "likes", "comments", "duration_s"):
            row[k] = _num(row.get(k))
        vps = row.get("views_per_sub")
        try:
            row["views_per_sub"] = float(vps) if vps not in (None, "") else ""
        except ValueError:
            row["views_per_sub"] = ""
    return rows


def classify(title: str) -> str:
    t = title.strip()
    low = t.lower()
    if low.startswith("why"):
        return "Why…"
    if low.startswith("what"):
        return "What…"
    if low.startswith("how"):
        return "How…"
    if low.startswith("when"):
        return "When…"
    if "?" in t:
        return "Other question"
    return "Statement / other"


def fmt_n(n) -> str:
    if n is None:
        return "—"
    return f"{n:,}"


def fmt_len(seconds) -> str:
    if not seconds:
        return "—"
    m, s = divmod(int(seconds), 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h}h {m}m"
    return f"{m}m {s:02d}s" if s else f"{m}m"


def median(xs: list[float]):
    return statistics.median(xs) if xs else None


def mean(xs: list[float]):
    return statistics.mean(xs) if xs else None


def parse_date(s: str):
    if not s:
        return None
    s = str(s).split("T")[0].replace("-", "")
    if len(s) >= 8 and s[:8].isdigit():
        return datetime.strptime(s[:8], "%Y%m%d")
    return None


def report(rows: list[dict]) -> str:
    lines = []
    by_ch = defaultdict(list)
    for row in rows:
        if row.get("id") and row.get("title") not in {"[Private video]", "[Deleted video]"}:
            by_ch[row.get("channel") or "unknown"].append(row)

    lines.append(f"# Channel research ({sum(len(v) for v in by_ch.values())} videos, {len(by_ch)} channel(s))\n")

    for channel, items in by_ch.items():
        views = [r["views"] for r in items if r.get("views") is not None]
        durs = [r["duration_s"] for r in items if r.get("duration_s")]
        dates = sorted(d for d in (parse_date(r.get("upload_date") or "") for r in items) if d)
        total = sum(views)
        items_sorted = sorted(items, key=lambda r: r.get("views") or 0, reverse=True)
        top3 = sum((r.get("views") or 0) for r in items_sorted[:3])
        share = (top3 / total * 100) if total else 0
        pace = "—"
        if len(dates) >= 2:
            days = max((dates[-1] - dates[0]).days, 1)
            per_week = len(dates) / (days / 7)
            pace = f"{per_week:.1f} videos/week"

        lines.append(f"## {channel}")
        lines.append("")
        lines.append("| Videos | Total views | Median | Mean | Median length | Top 3 share | Pace | Span |")
        lines.append("|---:|---:|---:|---:|---:|---:|---|---|")
        span = "—"
        if dates:
            span = f"{dates[0].date().isoformat()} → {dates[-1].date().isoformat()}"
        lines.append(
            f"| {len(items)} | {fmt_n(total)} | {fmt_n(int(median(views) or 0) if views else None)} "
            f"| {fmt_n(int(mean(views) or 0) if views else None)} | {fmt_len(median(durs))} "
            f"| {share:.0f}% | {pace} | {span} |"
        )
        lines.append("")

        lines.append("**Title patterns (median views)**")
        lines.append("")
        lines.append("| Pattern | n | Median views | Best |")
        lines.append("|---|---:|---:|---|")
        buckets = defaultdict(list)
        for r in items:
            buckets[classify(r.get("title") or "")].append(r)
        for pat, group in sorted(buckets.items(), key=lambda kv: median([x["views"] for x in kv[1] if x.get("views")] or [0]) or 0, reverse=True):
            vs = [x["views"] for x in group if x.get("views") is not None]
            best = max(group, key=lambda r: r.get("views") or 0)
            lines.append(f"| {pat} | {len(group)} | {fmt_n(int(median(vs) or 0) if vs else None)} | {fmt_n(best.get('views'))} |")
        lines.append("")

        def short_table(label, group):
            lines.append(f"**{label}**")
            lines.append("")
            lines.append("| Views | Length | Uploaded | Title |")
            lines.append("|---:|---:|---|---|")
            for r in group:
                d = parse_date(r.get("upload_date") or "")
                lines.append(
                    f"| {fmt_n(r.get('views'))} | {fmt_len(r.get('duration_s'))} "
                    f"| {d.date().isoformat() if d else '—'} | {(r.get('title') or '')[:80]} |"
                )
            lines.append("")

        short_table("Top 8", items_sorted[:8])
        if len(items_sorted) > 8:
            short_table("Bottom 4", list(reversed(items_sorted[-4:])))

        # Length vs views, rough buckets
        buckets_len = defaultdict(list)
        for r in items:
            d = r.get("duration_s") or 0
            if d < 60:
                key = "< 1 min"
            elif d < 8 * 60:
                key = "1–8 min"
            elif d < 15 * 60:
                key = "8–15 min"
            elif d < 30 * 60:
                key = "15–30 min"
            else:
                key = "30+ min"
            if r.get("views") is not None:
                buckets_len[key].append(r["views"])
        if buckets_len:
            lines.append("**Length vs median views**")
            lines.append("")
            lines.append("| Length | n | Median views |")
            lines.append("|---|---:|---:|")
            order = ["< 1 min", "1–8 min", "8–15 min", "15–30 min", "30+ min"]
            for key in order:
                vs = buckets_len.get(key)
                if vs:
                    lines.append(f"| {key} | {len(vs)} | {fmt_n(int(median(vs)))} |")
            lines.append("")

    lines.append(
        "Use these numbers to find gaps and title patterns. Write original scripts — "
        "do not copy titles or narration from the channels you study."
    )
    return "\n".join(lines) + "\n"


def fetch_subs(rows: list[dict], n: int, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    by_ch = defaultdict(list)
    for row in rows:
        if row.get("views") is not None:
            by_ch[row.get("channel") or "unknown"].append(row)
    for channel, items in by_ch.items():
        top = sorted(items, key=lambda r: r.get("views") or 0, reverse=True)[:n]
        for r in top:
            vid = r["id"]
            print(f"subs {channel} {vid}…", flush=True)
            proc = run_yt_dlp(
                [
                    "--skip-download",
                    "--write-auto-subs",
                    "--sub-langs",
                    "en.*,en",
                    "--sub-format",
                    "vtt",
                    "--no-warnings",
                    "-o",
                    str(dest / f"{vid}.%(ext)s"),
                    f"https://www.youtube.com/watch?v={vid}",
                ]
            )
            if proc.returncode != 0:
                print(f"warning: subs failed for {vid}: {proc.stderr.strip()}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channels", nargs="*", help="Channel URLs or @handles")
    ap.add_argument("--out", type=Path, default=Path("data"), help="Directory for CSV + report (default: data/)")
    ap.add_argument("--csv", type=Path, help="Analyze an existing CSV instead of pulling")
    ap.add_argument("--full", action="store_true", help="Fetch per-video metadata when the flat list is missing dates or duration")
    ap.add_argument("--subs", type=int, metavar="N", help="Download auto-subs for the top N videos per channel")
    ap.add_argument("--subs-dir", type=Path, default=None, help="Where to write auto-subs (default: <out>/subs)")
    args = ap.parse_args()

    if args.csv:
        rows = read_csv(args.csv)
        out_dir = args.out
        csv_path = args.csv
    else:
        if not args.channels:
            ap.error("pass channel URLs / @handles, or --csv")
        rows = []
        out_dir = args.out
        out_dir.mkdir(parents=True, exist_ok=True)
        for raw in args.channels:
            url = as_channel_url(raw)
            print(f"pulling {url}…", flush=True)
            entries, meta = load_entries(url)
            followers = _num(meta.get("followers"))
            chunk = enrich(entries, followers, full=args.full)
            for row in chunk:
                row["channel"] = row["channel"] or meta.get("channel") or channel_slug(url)
            rows.extend(chunk)
        csv_path = out_dir / "videos.csv"
        write_csv(csv_path, rows)
        print(f"wrote {csv_path} ({len(rows)} rows)", flush=True)

    text = report(rows)
    report_path = args.out / "report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    print(f"wrote {report_path}", flush=True)

    if args.subs:
        fetch_subs(rows, args.subs, args.subs_dir or (args.out / "subs"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
