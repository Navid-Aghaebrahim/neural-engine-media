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
import json
import os
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from ig_fal import generate_image

W = H = 1024

ACCENT1 = (16, 185, 129)   # teal (darker for light bg)
ACCENT2 = (99, 102, 241)   # indigo
GREY    = (75, 85, 99)     # slate-600
INK     = (17, 24, 39)     # near-black
WHITE   = (255, 255, 255)


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

THEMES = {
    "workflow": DEFAULT_SLIDES,
    "risk": [
        Slide(1, "Risk Management\nIs The Edge", "Signals are just the start."),
        Slide(2, "Don't Trust.\nVerify.", "AI suggests. You confirm."),
        Slide(3, "No Black Boxes.\nSee The Logic.", "Transparent pattern recognition."),
        Slide(4, "Protect Your Capital.\nTrade Responsibly.", "The most important rule."),
    ],
    "privacy": [
        Slide(1, "Your Data Stays\nOn Your Mac", "Zero cloud processing."),
        Slide(2, "Local-First\nArchitecture", "Speed + Privacy."),
        Slide(3, "No API Keys\nShared Externally", "Your broker connection is yours."),
        Slide(4, "Secure By Default.\nNeural-Engine.", "Trade with peace of mind."),
    ],
    "myths": [
        Slide(1, "Myth: AI Replaces\nThe Trader", "Reality: AI enhances the trader."),
        Slide(2, "Myth: Signals Are\nMagic Bullets", "Reality: They are probability filters."),
        Slide(3, "Myth: You Need\nA Supercomputer", "Reality: Optimized for Apple Silicon."),
        Slide(4, "Augmented Intelligence.\nNot Artificial Hype.", "Neural-Engine."),
    ],
    "features": [
        Slide(1, "Pattern Recognition\nIn Real-Time", "Catch setups you might miss."),
        Slide(2, "Multi-Timeframe\nAnalysis", "See the bigger picture."),
        Slide(3, "Native Mac App\nPerformance", "Butter smooth on M-series chips."),
        Slide(4, "Integrates With\nYour Workflow", "Seamless overlay technology."),
    ]
}


THEME_VISUALS = {
    "workflow": "clean white trading desk setup, minimalist monitor with trading charts, bright productivity aesthetic, soft shadows",
    "risk": "conceptual art of a golden shield protecting graph lines, bright airy composition, clean lines, security concept",
    "privacy": "clean silver vault door mechanism, bright metallic textures, secure enclave concept, white and grey tones",
    "myths": "bright lightbulb moment, clarity emerging from fog, sharp contrast, clean white studio lighting",
    "features": "clean technical wireframe of a stock chart, bright blueprint style, precision instruments, macro focus on data points",
}


def build_prompt(theme: str, variant: str) -> str:
    visual_cue = THEME_VISUALS.get(theme, "clean financial technology visualization")
    
    # Style A: Photorealistic, clean, bright
    base = (
        "High-quality photorealistic render for a fintech Instagram slide. "
        f"Subject: {visual_cue}. "
        "Lighting: Bright studio lighting, soft shadows, high key photography. "
        "Background: Clean WHITE or very light grey/blue. "
        "Style: Apple marketing aesthetic, premium, minimalist. "
        "Composition: Center-weighted, leaving negative space for text."
    )
    # Style B: 3D Illustration, bright
    artistic = (
        f"Premium 3D illustration of {theme} related to stock trading. "
        "Style: Claymorphism or clean 3D render, matte materials. "
        "Colors: White, soft blue, teal, pastel accents. "
        "Background: Pure white or soft gradient. "
        "Lighting: Bright, soft, directional." 
    )
    
    prompt = base if variant == "A" else artistic
    return prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pt_today())
    ap.add_argument("--slug", default="daily")
    ap.add_argument("--theme", default="workflow")
    ap.add_argument("--slides", type=int, default=4)
    ap.add_argument("--content", help="Path to JSON file with slide content [{'headline': '...', 'sub': '...'}, ...]")
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

    slides = []
    if args.content and os.path.exists(args.content):
        try:
            with open(args.content, "r") as f:
                data = json.load(f)
                for i, item in enumerate(data, start=1):
                    slides.append(Slide(i, item.get("headline", ""), item.get("sub", "")))
        except Exception as e:
            print(f"Error reading content file: {e}")
            slides = DEFAULT_SLIDES[: args.slides]
    else:
        # Fallback to hardcoded theme mapping
        base_slides = THEMES.get(theme)
        if not base_slides:
            # Fallback for unknown theme -> default slides
            base_slides = DEFAULT_SLIDES
        slides = base_slides[: args.slides]

    for idx, s in enumerate(slides, start=1):
        variant = "A" if random.random() < 0.7 else "B"
        prompt = build_prompt(theme=theme, variant=variant)
        bg = generate_image(prompt=prompt, model="fal-ai/flux/dev", image_size="square_hd")
        bg = bg.resize((W, H))

        draw = ImageDraw.Draw(bg)

        # badge
        theme_label = theme.upper().replace("_", " ")
        badge = f"NEURAL-ENGINE  |  {theme_label}"
        bb = badge_font.getbbox(badge)
        bw = (bb[2] - bb[0]) + 36
        bh = 36
        bx = (W - bw) // 2
        draw.rounded_rectangle([bx, 48, bx + bw, 48 + bh], radius=18, fill=(*ACCENT2, 40), outline=(*ACCENT2, 140), width=1)
        draw.text(((W - (bb[2]-bb[0]))//2, 56), badge, font=badge_font, fill=ACCENT1)

        # TEXT LAYOUT (Vertical Center)
        # Calculate total height of text block first
        total_h = 0
        headline_lines = s.headline.split("\n")
        
        # Measure headline
        h_metrics = []
        for line in headline_lines:
            bb = h_font.getbbox(line)
            h_metrics.append((line, bb[2]-bb[0], bb[3]-bb[1]))
            total_h += (bb[3]-bb[1]) + 12 # line gap
        
        total_h += 24 # gap to sub
        
        # Measure sub
        sb = sub_font.getbbox(s.sub)
        sub_w = sb[2] - sb[0]
        sub_h = sb[3] - sb[1]
        total_h += sub_h
        
        # Start Y position for vertical centering
        start_y = (H - total_h) // 2
        
        # Optional: Add a subtle gradient/blur backing behind text for readability?
        # For now, let's just use a semi-transparent dark box if background is busy
        # But we don't know if bg is busy. Let's assume the prompt handles "clean area".
        # Better: Drop shadow for text.

        # Draw Headline
        y = start_y
        for line, w, h in h_metrics:
            # No shadow needed for clean white background, maybe subtle glow if needed
            # draw.text(((W - w)//2 + 2, y + 2), line, font=h_font, fill=(200,200,200)) 
            # Text (Dark Ink)
            draw.text(((W - w)//2, y), line, font=h_font, fill=INK)
            y += h + 12
        
        # Draw Sub (with pill)
        y += 12
        # Pill background for sub (Light grey/blue for contrast)
        pill_pad_x = 24
        pill_pad_y = 12
        pill_x = (W - sub_w) // 2
        draw.rounded_rectangle(
            [pill_x - pill_pad_x, y - pill_pad_y, pill_x + sub_w + pill_pad_x, y + sub_h + pill_pad_y],
            radius=16,
            fill=(243, 244, 246, 255) # Gray-100
        )
        draw.text(((W - sub_w)//2, y), s.sub, font=sub_font, fill=ACCENT2)

        # slide number
        num = f"{idx:02d}/{len(slides):02d}"
        nf = load_font(18, bold=True)
        nb = nf.getbbox(num)
        draw.rounded_rectangle([48, 52, 48 + (nb[2]-nb[0]) + 22, 52 + 30], radius=15, fill=(255, 255, 255, 220), outline=(229, 231, 235, 255), width=1)
        draw.text((58, 57), num, font=nf, fill=GREY)

        # footer
        brand_y = H - 80
        draw.line([(52, brand_y - 14), (W - 52, brand_y - 14)], fill=(229, 231, 235, 255), width=1)
        draw.text((52, brand_y), "NEURAL-ENGINE", font=footer_font, fill=INK)
        disc = "Not financial advice. Trade responsibly."
        db = disc_font.getbbox(disc)
        draw.text((W - (db[2]-db[0]) - 52, brand_y + 4), disc, font=disc_font, fill=GREY)

        out = f"assets/ig/{date}-AM-{slug}-S{idx:02d}.png"
        bg.convert("RGB").save(out, "PNG")
        print(f"Saved: {out} (variant={variant})")


if __name__ == "__main__":
    main()
