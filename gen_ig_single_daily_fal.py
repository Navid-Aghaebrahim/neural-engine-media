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


def build_prompt(kind: str) -> str:
    base = (
        "Square 1024x1024 background for a premium fintech Instagram post. "
        "Clean WHITE / light background, subtle light-gray chart motif, soft teal/indigo accents, minimal editorial. "
        "Very high readability in the center. "
        "No text, no logos, no watermark."
    )
    artistic = " Slightly more artistic: gentle gradients, subtle paper texture, modern glassmorphism shapes — keep it LIGHT and professional."
    if kind == "A":
        return base
    if kind == "B":
        return base + artistic
    return base + artistic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pt_today())
    ap.add_argument("--slug", default="daily")
    ap.add_argument("--headline", default="Signals. Not Noise.")
    ap.add_argument("--sub", default="AI overlay inside TradingView. You stay in control.")
    args = ap.parse_args()

    variant = "A" if random.random() < 0.6 else "B"  # blend
    prompt = build_prompt(variant)

    img = generate_image(prompt=prompt, model="fal-ai/flux/dev", image_size="square_hd")
    img = img.resize((W, H))

    draw = ImageDraw.Draw(img)

    badge_font = load_font(19, bold=True)
    h_font = load_font(64, bold=True)
    sub_font = load_font(28, bold=False)
    footer_font = load_font(21, bold=True)
    disc_font = load_font(16, bold=False)

    badge = "NEURAL-ENGINE  |  DAILY"
    bb = badge_font.getbbox(badge)
    bw = (bb[2]-bb[0]) + 36
    bh = 36
    bx = (W - bw)//2
    draw.rounded_rectangle([bx, 48, bx+bw, 48+bh], radius=18, fill=(*ACCENT1, 30), outline=(*ACCENT1, 140), width=1)
    draw.text(((W-(bb[2]-bb[0]))//2, 56), badge, font=badge_font, fill=ACCENT2)

    # Headline
    y = 150
    for line in args.headline.split("\n"):
        hb = h_font.getbbox(line)
        draw.text(((W-(hb[2]-hb[0]))//2, y), line, font=h_font, fill=INK)
        y += (hb[3]-hb[1]) + 8

    # Subheadline
    sub_lines = wrap_text(args.sub, sub_font, 900)
    for ln in sub_lines:
        sb = sub_font.getbbox(ln)
        draw.text(((W-(sb[2]-sb[0]))//2, y+10), ln, font=sub_font, fill=GREY)
        y += (sb[3]-sb[1]) + 8

    # CTA pill
    cta = "Join the waitlist → neural-engine.ai"
    cta_font = load_font(28, bold=True)
    cb = cta_font.getbbox(cta)
    cw = (cb[2]-cb[0]) + 44
    ch = 56
    cx = (W - cw)//2
    cy = H - 210
    draw.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=18, fill=(*ACCENT2, 35), outline=(*ACCENT2, 140), width=2)
    draw.text(((W-(cb[2]-cb[0]))//2, cy+14), cta, font=cta_font, fill=INK)

    # footer
    brand_y = H - 80
    draw.line([(52, brand_y - 14), (W - 52, brand_y - 14)], fill=(229, 231, 235, 255), width=1)
    draw.text((52, brand_y), "NEURAL-ENGINE", font=footer_font, fill=INK)
    disc = "Not financial advice. Trade responsibly."
    db = disc_font.getbbox(disc)
    draw.text((W-(db[2]-db[0])-52, brand_y+4), disc, font=disc_font, fill=GREY)

    os.makedirs("assets/ig", exist_ok=True)
    out = f"assets/ig/{args.date}-PM-{args.slug}.png"
    img.convert("RGB").save(out, "PNG")
    print(f"Saved: {out} (variant={variant})")


if __name__ == "__main__":
    main()
