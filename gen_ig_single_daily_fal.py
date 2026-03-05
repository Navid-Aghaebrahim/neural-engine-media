#!/usr/bin/env python3
"""Neural-Engine IG Single (daily PM) — fal.ai background + Pillow text.

Saves: assets/ig/YYYY-MM-DD-PM-<slug>.png
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import random

from PIL import Image, ImageDraw, ImageFont

from ig_fal import generate_image

W = H = 1024
ACCENT1 = (16, 185, 129)   # teal (darker for light bg)
ACCENT2 = (99, 102, 241)   # indigo
GOLD    = (245, 158, 11)
WHITE   = (255, 255, 255)
GREY    = (75, 85, 99)
INK     = (17, 24, 39)


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
    "workflow": "clean white trading desk setup, minimalist monitor with trading charts, bright productivity aesthetic, soft shadows",
    "risk": "conceptual art of a golden shield protecting graph lines, bright airy composition, clean lines, security concept",
    "privacy": "clean silver vault door mechanism, bright metallic textures, secure enclave concept, white and grey tones",
    "myths": "bright lightbulb moment, clarity emerging from fog, sharp contrast, clean white studio lighting",
    "features": "clean technical wireframe of a stock chart, bright blueprint style, precision instruments, macro focus on data points",
}


def build_prompt(theme: str) -> str:
    visual_cue = THEME_VISUALS.get(theme, "clean financial technology visualization")
    
    # Style: Photorealistic, clean, bright (Apple Marketing Aesthetic)
    prompt = (
        "High-quality photorealistic render for a fintech Instagram slide. "
        f"Subject: {visual_cue}. "
        "Lighting: Bright studio lighting, soft shadows, high key photography. "
        "Background: Clean WHITE or very light grey/blue. "
        "Style: Apple marketing aesthetic, premium, minimalist. "
        "Composition: Center-weighted, leaving negative space for text."
    )
    return prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pt_today())
    ap.add_argument("--slug", default="daily")
    ap.add_argument("--theme", default="workflow", help="workflow|risk|privacy|myths|features")
    ap.add_argument("--headline", default="Signals. Not Noise.")
    ap.add_argument("--sub", default="AI overlay inside TradingView. You stay in control.")
    args = ap.parse_args()

    # Generate Image
    prompt = build_prompt(theme=args.theme)
    img = generate_image(prompt=prompt, model="fal-ai/flux/dev", image_size="square_hd")
    img = img.resize((W, H))

    draw = ImageDraw.Draw(img)

    badge_font = load_font(19, bold=True)
    h_font = load_font(64, bold=True)
    sub_font = load_font(28, bold=False)
    footer_font = load_font(21, bold=True)
    disc_font = load_font(16, bold=False)

    # Badge (Top)
    theme_label = args.theme.upper()
    badge = f"NEURAL-ENGINE  |  {theme_label}"
    bb = badge_font.getbbox(badge)
    bw = (bb[2]-bb[0]) + 36
    bh = 36
    bx = (W - bw)//2
    draw.rounded_rectangle([bx, 48, bx+bw, 48+bh], radius=18, fill=(*ACCENT1, 30), outline=(*ACCENT1, 140), width=1)
    draw.text(((W-(bb[2]-bb[0]))//2, 56), badge, font=badge_font, fill=ACCENT2)

    # TEXT LAYOUT (Vertical Center)
    total_h = 0
    headline_lines = args.headline.split("\\n") # Handle escaped newlines
    if len(headline_lines) == 1:
         headline_lines = wrap_text(args.headline, h_font, 900)

    # Measure Headline
    h_metrics = []
    for line in headline_lines:
        bb = h_font.getbbox(line)
        h_metrics.append((line, bb[2]-bb[0], bb[3]-bb[1]))
        total_h += (bb[3]-bb[1]) + 12

    total_h += 24 # gap to sub

    # Measure Sub
    sub_lines = wrap_text(args.sub, sub_font, 850)
    sub_metrics = []
    for line in sub_lines:
        sb = sub_font.getbbox(line)
        sub_metrics.append((line, sb[2]-sb[0], sb[3]-sb[1]))
        total_h += (sb[3]-sb[1]) + 8

    # Start Y
    start_y = (H - total_h) // 2
    
    # Draw Headline
    y = start_y
    for line, w, h in h_metrics:
        # No shadow needed for clean white bg
        draw.text(((W - w)//2, y), line, font=h_font, fill=INK)
        y += h + 12

    # Draw Sub (with pill background)
    y += 12
    # Calculate pill size
    pill_w = max([m[1] for m in sub_metrics]) + 48
    pill_h = (len(sub_metrics) * (sub_metrics[0][2] + 8)) + 16
    pill_x = (W - pill_w) // 2
    
    draw.rounded_rectangle(
        [pill_x, y - 12, pill_x + pill_w, y + pill_h - 12],
        radius=16,
        fill=(243, 244, 246, 255) # Gray-100
    )
    
    # Draw sub text inside pill
    for line, w, h in sub_metrics:
        draw.text(((W - w)//2, y), line, font=sub_font, fill=ACCENT2)
        y += h + 8

    # CTA pill (Bottom)
    cta = "Join the waitlist → neural-engine.tech"
    cta_font = load_font(28, bold=True)
    cb = cta_font.getbbox(cta)
    cw = (cb[2]-cb[0]) + 44
    ch = 56
    cx = (W - cw)//2
    cy = H - 210
    draw.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=18, fill=(*ACCENT2, 35), outline=(*ACCENT2, 140), width=2)
    draw.text(((W-(cb[2]-cb[0]))//2, cy+14), cta, font=cta_font, fill=INK)

    # Footer
    brand_y = H - 80
    draw.line([(52, brand_y - 14), (W - 52, brand_y - 14)], fill=(229, 231, 235, 255), width=1)
    draw.text((52, brand_y), "NEURAL-ENGINE", font=footer_font, fill=INK)
    disc = "Not financial advice. Trade responsibly."
    db = disc_font.getbbox(disc)
    draw.text((W-(db[2]-db[0])-52, brand_y+4), disc, font=disc_font, fill=GREY)

    os.makedirs("assets/ig", exist_ok=True)
    out = f"assets/ig/{args.date}-PM-{args.slug}.png"
    img.convert("RGB").save(out, "PNG")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
