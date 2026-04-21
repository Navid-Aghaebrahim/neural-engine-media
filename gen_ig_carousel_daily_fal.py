#!/usr/bin/env python3
"""Neural-Engine IG Carousel (daily) — fal.ai backgrounds + Pillow text.

Improved for:
- stronger creative rotation
- tighter educational/ad balance
- deterministic readability panels
- copy length QA
- less repetitive hooks/themes
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from ig_fal import generate_image
from ig_strategy import (
    SlidePlan,
    build_carousel_plan,
    ensure_distinct_copy,
    save_recent,
    validate_slide_copy,
)

W = H = 1024
ACCENT1 = (16, 185, 129)
ACCENT2 = (99, 102, 241)
GREY = (75, 85, 99)
INK = (17, 24, 39)
WHITE = (255, 255, 255)
SOFT_BG = (255, 255, 255, 232)
PILL_BG = (243, 244, 246, 248)


def pt_today() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        f"/System/Library/Fonts/{'SFProDisplay-Bold' if bold else 'SFProDisplay-Regular'}.otf",
        f"/System/Library/Fonts/{'SFProText-Bold' if bold else 'SFProText-Regular'}.otf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bb = font.getbbox(test)
        if bb[2] - bb[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


@dataclass
class Slide:
    number: int
    headline: str
    sub: str


THEMES = {
    "workflow": "minimal trading workspace, bright premium desk scene, negative space for typography",
    "risk": "risk-management editorial concept, clean geometric design, bright premium aesthetic",
    "privacy": "local-first computing concept, silver laptop, soft white and gray palette, minimal composition",
    "myths": "clarity versus noise concept art, premium editorial fintech look, clean background",
    "features": "chart-analysis workspace with refined composition, bright minimal lighting",
}


def build_prompt(theme: str, variant: str) -> str:
    visual_cue = THEMES.get(theme, "clean financial technology visualization")
    style = "photorealistic premium editorial" if variant == "A" else "minimal 3D premium illustration"
    return (
        "Create a premium Instagram carousel background for a fintech brand. "
        f"Subject: {visual_cue}. Style: {style}. "
        "Important: NO text, NO letters, NO numbers, NO logos, NO watermarks. "
        "Use bright high-key lighting, very light backgrounds, minimal clutter, and a calm center area. "
        "Make it visually distinct from a generic trading ad and keep strong negative space for overlaid copy."
    )


def draw_readability_panel(draw: ImageDraw.ImageDraw) -> tuple[int, int, int, int]:
    panel = (84, 150, W - 84, H - 210)
    draw.rounded_rectangle(panel, radius=34, fill=SOFT_BG, outline=(229, 231, 235, 255), width=2)
    return panel


def parse_slides(args) -> list[Slide]:
    slides: list[Slide] = []
    if args.content and os.path.exists(args.content):
        with open(args.content, "r") as f:
            data = json.load(f)
        for i, item in enumerate(data, start=1):
            slides.append(Slide(i, item.get("headline", ""), item.get("sub", "")))
        return slides

    strategy, plan_slides = build_carousel_plan(args.theme)
    args._strategy = strategy
    return [Slide(i, s.headline, s.sub) for i, s in enumerate(plan_slides, start=1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pt_today())
    ap.add_argument("--slug", default="daily")
    ap.add_argument("--theme", default="workflow")
    ap.add_argument("--slides", type=int, default=4)
    ap.add_argument("--content", help="Path to JSON file with slide content [{'headline': '...', 'sub': '...'}, ...]")
    args = ap.parse_args()

    os.makedirs("assets/ig", exist_ok=True)

    badge_font = load_font(19, bold=True)
    h_font = load_font(56, bold=True)
    sub_font = load_font(28, bold=False)
    footer_font = load_font(21, bold=True)
    disc_font = load_font(16, bold=False)

    slides = parse_slides(args)[: args.slides]

    qa_issues = []
    for slide in slides:
        qa_issues.extend(validate_slide_copy(slide.headline, slide.sub))
    qa_issues.extend(ensure_distinct_copy([s.headline for s in slides]))
    if qa_issues:
        raise SystemExit(f"Copy QA failed: {', '.join(sorted(set(qa_issues)))}")

    for idx, s in enumerate(slides, start=1):
        variant = "A" if random.random() < 0.6 else "B"
        prompt = build_prompt(theme=args.theme, variant=variant)
        bg = generate_image(prompt=prompt, model="fal-ai/flux/dev", image_size="square_hd")
        bg = bg.resize((W, H))
        draw = ImageDraw.Draw(bg)

        theme_label = args.theme.upper().replace("_", " ")
        badge = f"NEURAL-ENGINE  |  {theme_label}"
        bb = badge_font.getbbox(badge)
        bw = (bb[2] - bb[0]) + 36
        bx = (W - bw) // 2
        draw.rounded_rectangle([bx, 48, bx + bw, 84], radius=18, fill=(255, 255, 255, 215), outline=(209, 213, 219, 255), width=1)
        draw.text(((W - (bb[2] - bb[0])) // 2, 56), badge, font=badge_font, fill=ACCENT2)

        panel_left, panel_top, panel_right, panel_bottom = draw_readability_panel(draw)

        headline_lines = wrap_text(s.headline, h_font, 760)
        sub_lines = wrap_text(s.sub, sub_font, 680)
        headline_h = sum((h_font.getbbox(line)[3] - h_font.getbbox(line)[1]) + 10 for line in headline_lines)
        sub_h = sum((sub_font.getbbox(line)[3] - sub_font.getbbox(line)[1]) + 8 for line in sub_lines)
        total_h = headline_h + 30 + sub_h
        y = panel_top + max(44, ((panel_bottom - panel_top) - total_h) // 2)

        for line in headline_lines:
            bb = h_font.getbbox(line)
            w = bb[2] - bb[0]
            h = bb[3] - bb[1]
            draw.text(((W - w) // 2, y), line, font=h_font, fill=INK)
            y += h + 10

        y += 14
        max_sub_w = max(sub_font.getbbox(line)[2] - sub_font.getbbox(line)[0] for line in sub_lines)
        pill_w = max_sub_w + 52
        pill_h = sub_h + 18
        pill_x = (W - pill_w) // 2
        draw.rounded_rectangle([pill_x, y - 10, pill_x + pill_w, y - 10 + pill_h], radius=18, fill=PILL_BG)
        for line in sub_lines:
            bb = sub_font.getbbox(line)
            w = bb[2] - bb[0]
            h = bb[3] - bb[1]
            draw.text(((W - w) // 2, y), line, font=sub_font, fill=ACCENT2)
            y += h + 8

        num = f"{idx:02d}/{len(slides):02d}"
        nf = load_font(18, bold=True)
        nb = nf.getbbox(num)
        draw.rounded_rectangle([48, 52, 48 + (nb[2] - nb[0]) + 22, 82], radius=15, fill=(255, 255, 255, 220), outline=(229, 231, 235, 255), width=1)
        draw.text((58, 57), num, font=nf, fill=GREY)

        brand_y = H - 80
        draw.line([(52, brand_y - 14), (W - 52, brand_y - 14)], fill=(229, 231, 235, 255), width=1)
        draw.text((52, brand_y), "NEURAL-ENGINE", font=footer_font, fill=INK)
        disc = "Not financial advice. Trade responsibly."
        db = disc_font.getbbox(disc)
        draw.text((W - (db[2] - db[0]) - 52, brand_y + 4), disc, font=disc_font, fill=GREY)

        out = f"assets/ig/{args.date}-AM-{args.slug}-S{idx:02d}.png"
        bg.convert("RGB").save(out, "PNG")
        print(f"Saved: {out} (variant={variant})")

    strategy = getattr(args, "_strategy", None)
    if strategy:
        save_recent(strategy, slides=[SlidePlan(s.headline, s.sub) for s in slides])
        print(f"Strategy: {strategy.post_type} | hook={strategy.hook}")


if __name__ == "__main__":
    main()
