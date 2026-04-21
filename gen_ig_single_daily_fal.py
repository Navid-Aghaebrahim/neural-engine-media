#!/usr/bin/env python3
"""Neural-Engine IG Single (daily PM) — fal.ai background + Pillow text.

Saves: assets/ig/YYYY-MM-DD-PM-<slug>.png
"""

from __future__ import annotations

import argparse
import datetime as dt
import os

from PIL import Image, ImageDraw, ImageFont

from ig_fal import generate_image
from ig_strategy import build_single_plan, save_recent, validate_single_copy

W = H = 1024
ACCENT1 = (16, 185, 129)
ACCENT2 = (99, 102, 241)
WHITE = (255, 255, 255)
GREY = (75, 85, 99)
INK = (17, 24, 39)
SOFT_BG = (255, 255, 255, 232)
PILL_BG = (243, 244, 246, 245)
CTA_BG = (225, 232, 255, 245)


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
    lines = []
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


THEME_VISUALS = {
    "workflow": "minimalist trading desk, bright daylight, premium fintech aesthetic, clean monitor composition, lots of negative space",
    "risk": "abstract risk management concept, premium editorial fintech look, bright background, geometric composition, safe space for typography",
    "privacy": "clean local-first computing setup, silver laptop, subtle security symbolism, soft white palette, negative space for text",
    "myths": "editorial concept image about clarity vs noise, bright studio lighting, minimalist premium composition",
    "features": "premium chart-analysis workspace, clean high-key lighting, restrained fintech visual, simple background",
}


def build_prompt(theme: str) -> str:
    visual_cue = THEME_VISUALS.get(theme, "clean financial technology visualization")
    return (
        "Create a premium Instagram background for a fintech brand. "
        f"Subject: {visual_cue}. "
        "Important: NO text, NO letters, NO numbers, NO UI labels, NO watermarks. "
        "Use bright high-key lighting, soft shadows, minimal clutter, premium Apple-like art direction. "
        "Keep the center area calm and simple so overlaid text stays readable. "
        "Favor white, pale gray, light blue, and subtle teal accents."
    )


def draw_readability_panel(draw: ImageDraw.ImageDraw) -> tuple[int, int, int, int]:
    panel = (88, 140, W - 88, H - 250)
    draw.rounded_rectangle(panel, radius=36, fill=SOFT_BG, outline=(229, 231, 235, 255), width=2)
    return panel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pt_today())
    ap.add_argument("--slug", default="daily")
    ap.add_argument("--theme", default="workflow", help="workflow|risk|privacy|myths|features")
    ap.add_argument("--headline")
    ap.add_argument("--sub")
    ap.add_argument("--cta")
    args = ap.parse_args()

    strategy, auto_plan = build_single_plan(args.theme)
    headline = args.headline or auto_plan.headline
    sub = args.sub or auto_plan.sub
    cta = args.cta or auto_plan.cta

    issues = validate_single_copy(headline, sub, cta)
    if issues:
        raise SystemExit(f"Copy QA failed: {', '.join(issues)}")

    prompt = build_prompt(theme=args.theme)
    img = generate_image(prompt=prompt, model="fal-ai/flux/dev", image_size="square_hd")
    img = img.resize((W, H))

    draw = ImageDraw.Draw(img)

    badge_font = load_font(19, bold=True)
    h_font = load_font(60, bold=True)
    sub_font = load_font(28, bold=False)
    cta_font = load_font(28, bold=True)
    footer_font = load_font(21, bold=True)
    disc_font = load_font(16, bold=False)

    theme_label = args.theme.upper()
    badge = f"NEURAL-ENGINE  |  {theme_label}"
    bb = badge_font.getbbox(badge)
    bw = (bb[2] - bb[0]) + 36
    bx = (W - bw) // 2
    draw.rounded_rectangle([bx, 48, bx + bw, 84], radius=18, fill=(255, 255, 255, 215), outline=(209, 213, 219, 255), width=1)
    draw.text(((W - (bb[2] - bb[0])) // 2, 56), badge, font=badge_font, fill=ACCENT2)

    panel_left, panel_top, panel_right, panel_bottom = draw_readability_panel(draw)

    headline_lines = wrap_text(headline, h_font, 760)
    sub_lines = wrap_text(sub, sub_font, 700)

    headline_h = sum((h_font.getbbox(line)[3] - h_font.getbbox(line)[1]) + 10 for line in headline_lines)
    sub_h = sum((sub_font.getbbox(line)[3] - sub_font.getbbox(line)[1]) + 8 for line in sub_lines)
    total_h = headline_h + 28 + sub_h + 110
    y = panel_top + max(36, ((panel_bottom - panel_top) - total_h) // 2)

    for line in headline_lines:
        bb = h_font.getbbox(line)
        w = bb[2] - bb[0]
        h = bb[3] - bb[1]
        draw.text(((W - w) // 2, y), line, font=h_font, fill=INK)
        y += h + 10

    y += 12
    max_sub_w = max(sub_font.getbbox(line)[2] - sub_font.getbbox(line)[0] for line in sub_lines)
    pill_w = max_sub_w + 56
    pill_h = sub_h + 20
    pill_x = (W - pill_w) // 2
    draw.rounded_rectangle([pill_x, y - 10, pill_x + pill_w, y - 10 + pill_h], radius=20, fill=PILL_BG)
    for line in sub_lines:
        bb = sub_font.getbbox(line)
        w = bb[2] - bb[0]
        h = bb[3] - bb[1]
        draw.text(((W - w) // 2, y), line, font=sub_font, fill=ACCENT2)
        y += h + 8

    cta_bb = cta_font.getbbox(cta)
    cta_w = (cta_bb[2] - cta_bb[0]) + 46
    cta_x = (W - cta_w) // 2
    cta_y = panel_bottom - 84
    draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + 56], radius=18, fill=CTA_BG, outline=(184, 198, 255, 255), width=2)
    draw.text(((W - (cta_bb[2] - cta_bb[0])) // 2, cta_y + 14), cta, font=cta_font, fill=INK)

    brand_y = H - 80
    draw.line([(52, brand_y - 14), (W - 52, brand_y - 14)], fill=(229, 231, 235, 255), width=1)
    draw.text((52, brand_y), "NEURAL-ENGINE", font=footer_font, fill=INK)
    disc = "Not financial advice. Trade responsibly."
    db = disc_font.getbbox(disc)
    draw.text((W - (db[2] - db[0]) - 52, brand_y + 4), disc, font=disc_font, fill=GREY)

    os.makedirs("assets/ig", exist_ok=True)
    out = f"assets/ig/{args.date}-PM-{args.slug}.png"
    img.convert("RGB").save(out, "PNG")
    save_recent(strategy, single=auto_plan)
    print(f"Saved: {out}")
    print(f"Strategy: {strategy.post_type} | hook={strategy.hook}")


if __name__ == "__main__":
    main()
