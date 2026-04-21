#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from ig_strategy import build_caption, build_carousel_plan, build_single_plan, save_recent

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets" / "ig"
OUT = ROOT / "tmp" / "ig_samples"


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    themes = ["workflow", "risk", "features"]
    samples: list[dict] = []

    for idx, theme in enumerate(themes, start=1):
        plan, slides = build_carousel_plan(theme, seed=idx)
        slug = f"sample-{idx}-{theme}"
        content_path = OUT / f"{slug}-carousel.json"
        content_path.write_text(json.dumps([s.__dict__ for s in slides], indent=2))
        run([sys.executable, "gen_ig_carousel_daily_fal.py", "--theme", theme, "--slug", slug, "--content", str(content_path)])
        caption = build_caption(plan, kind="carousel")
        (OUT / f"{slug}-carousel-caption.txt").write_text(caption)
        save_recent(plan, slides=slides, caption=caption)
        samples.append({
            "theme": theme,
            "kind": "carousel",
            "slug": slug,
            "caption_file": str((OUT / f"{slug}-carousel-caption.txt").relative_to(ROOT)),
        })

    for idx, theme in enumerate(themes, start=1):
        plan, single = build_single_plan(theme, seed=100 + idx)
        slug = f"sample-{idx}-{theme}-single"
        run([
            sys.executable,
            "gen_ig_single_daily_fal.py",
            "--theme",
            theme,
            "--slug",
            slug,
            "--headline",
            single.headline,
            "--sub",
            single.sub,
            "--cta",
            single.cta,
        ])
        caption = build_caption(plan, kind="single")
        (OUT / f"{slug}-caption.txt").write_text(caption)
        save_recent(plan, single=single, caption=caption)
        samples.append({
            "theme": theme,
            "kind": "single",
            "slug": slug,
            "caption_file": str((OUT / f"{slug}-caption.txt").relative_to(ROOT)),
        })

    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(samples, indent=2))
    print(f"Wrote sample manifest: {manifest}")


if __name__ == "__main__":
    main()
