#!/usr/bin/env python3
"""Neural-Engine IG Carousel (daily) — fal.ai backgrounds + Pillow text.

- Uses fal.ai (flux/dev) to generate a background (style A/B blend)
- Overlays crisp text/footer/disclaimer with Pillow
- Saves slides to assets/ig/YYYY-MM-DD-AM-<slug>-S01..S0N.png

This is designed to be called from the 9AM cron job.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from ig_fal import generate_image

W = H = 1024

ACCENT1 = (94, 234, 212)   # teal
ACCENT2 = (139, 92, 246)   # violet
GREY = (160, 170, 200)
WHITE = (255, 255, 255)


def pt_today() -> str:
    # Cron runs in PT on the host
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


def draw_centered(draw: ImageDraw.ImageDraw, text: str, y: int, font: ImageFont.ImageFont, fill, max_w: int = 900, line_gap: int = 10) -> int:
    lines = wrap_text(text, font, max_w)
    lh = (font.getbbox("Ag")[3] - font.getbbox("Ag")[1]) + line_gap
    for i, ln in enumerate(lines):
        bb = font.getbbox(ln)
        lw = bb[2] - bb[0]
        draw.text(((W - lw) // 2, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


@dataclass
class Slide:
    number: int
    headline: str
    sub: str


DEFAULT_SLIDES = [
    Slide(1, "Your Trading Day,\nSupercharged With AI", "Same charts. Smarter layer."),
    Slide(2, "Signals Overlay\nInside TradingView", "You analyze. You decide."),
    Slide(3, "Runs Locally\nOn Your Mac", "Privacy-first by design."),
    Slide(4, "No Auto-Trading.\n100% Your Call.", "Risk stays with you."),
]


def build_prompt(theme: str, variant: str) -> str:
    # Style A: clean, brand-safe
    base = (
        "Square 1024x1024 background for a fintech Instagram slide. "
        "Dark navy gradient, subtle chart motif, soft teal/violet glow accents, minimalist, clean. "
        "No text, no logos, no watermark, no UI." 
    )
    # Style B: more artistic
    artistic = (
        "Cinematic lighting, higher contrast, abstract glassmorphism shapes, modern editorial design." 
    )
    if variant == "A":
        return base + f" Theme: {theme}."
    if variant == "B":
        return base + artistic + f" Theme: {theme}."
    # Blend
    return base + artistic + f" Theme: {theme}."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pt_today())
    ap.add_argument("--slug", default="daily")
    ap.add_argument("--theme", default="workflow")
    ap.add_argument("--slides", type=int, default=4)
    args = ap.parse_args()

    date = args.date
    slug = args.slug
    theme = args.theme

    # A/B blend: 70% A, 30% B per slide
    os.makedirs("assets/ig", exist_ok=True)

    badge_font = load_font(19, bold=True)
    h_font = load_font(62, bold=True)
    sub_font = load_font(28, bold=False)
    footer_font = load_font(21, bold=True)
    disc_font = load_font(16, bold=False)

    slides = DEFAULT_SLIDES[: args.slides]

    for idx, s in enumerate(slides, start=1):
        variant = "A" if random.random() < 0.7 else "B"
        prompt = build_prompt(theme=theme, variant=variant)
        bg = generate_image(prompt=prompt, model="fal-ai/flux/dev", image_size="square_hd")
        bg = bg.resize((W, H))

        draw = ImageDraw.Draw(bg)

        # badge
        badge = "NEURAL-ENGINE  |  WORKFLOW"
        bb = badge_font.getbbox(badge)
        bw = (bb[2] - bb[0]) + 36
        bh = 36
        bx = (W - bw) // 2
        draw.rounded_rectangle([bx, 48, bx + bw, 48 + bh], radius=18, fill=(*ACCENT2, 40), outline=(*ACCENT2, 140), width=1)
        draw.text(((W - (bb[2]-bb[0]))//2, 56), badge, font=badge_font, fill=ACCENT1)

        # headline
        y = 118
        for line in s.headline.split("\n"):
            hb = h_font.getbbox(line)
            draw.text(((W - (hb[2]-hb[0]))//2, y), line, font=h_font, fill=WHITE)
            y += (hb[3]-hb[1]) + 6

        # sub
        sb = sub_font.getbbox(s.sub)
        draw.text(((W - (sb[2]-sb[0]))//2, y + 10), s.sub, font=sub_font, fill=GREY)

        # slide number
        num = f"{idx:02d}/{len(slides):02d}"
        nf = load_font(18, bold=True)
        nb = nf.getbbox(num)
        draw.rounded_rectangle([48, 52, 48 + (nb[2]-nb[0]) + 22, 52 + 30], radius=15, fill=(16, 22, 50, 220))
        draw.text((58, 57), num, font=nf, fill=GREY)

        # footer
        brand_y = H - 80
        draw.line([(52, brand_y - 14), (W - 52, brand_y - 14)], fill=(*ACCENT2, 100), width=1)
        draw.text((52, brand_y), "NEURAL-ENGINE", font=footer_font, fill=ACCENT1)
        disc = "Not financial advice. Trade responsibly."
        db = disc_font.getbbox(disc)
        draw.text((W - (db[2]-db[0]) - 52, brand_y + 4), disc, font=disc_font, fill=GREY)

        out = f"assets/ig/{date}-AM-{slug}-S{idx:02d}.png"
        bg.convert("RGB").save(out, "PNG")
        print(f"Saved: {out} (variant={variant})")


if __name__ == "__main__":
    main()
