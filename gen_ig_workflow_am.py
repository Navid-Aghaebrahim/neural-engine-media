#!/usr/bin/env python3
"""
Neural-Engine IG Carousel — 2026-02-26 AM
Theme: Workflow — "The Trading Workflow Neural-Engine Fits Into"
4 slides
"""

import os, sys, math
from PIL import Image, ImageDraw, ImageFont

DATE   = "2026-02-26"
SLUG   = "workflow-daily-routine"
W, H   = 1024, 1024

# ── Colours ───────────────────────────────────────────────────────────────────
BG_TOP    = (6,  8,  20)
BG_BOT    = (12, 18,  44)
ACCENT1   = (94, 234, 212)      # teal
ACCENT2   = (139, 92, 246)      # violet
GOLD      = (251, 191, 36)
WHITE     = (255, 255, 255)
GREY      = (155, 165, 195)
DARK_CARD = (16, 22, 50)

# ── Slide definitions ─────────────────────────────────────────────────────────
SLIDES = [
    {
        "badge":   "🔄  WORKFLOW  |  NEURAL-ENGINE",
        "number":  "01",
        "head":    "Your Trading Day,\nSupercharged With AI",
        "sub":     "The same charts. A smarter layer on top.",
        "bullets": [],
        "accent":  ACCENT2,
        "glow_l":  (ACCENT1, 200, 820),
        "glow_r":  (ACCENT2, 820, 160),
        "chart":   True,
    },
    {
        "badge":   "🔄  WORKFLOW  |  NEURAL-ENGINE",
        "number":  "02",
        "head":    "Step 1: Open TradingView.\nNeural-Engine Loads.",
        "sub":     "No plugins. No cloud account. Just launch and go.",
        "bullets": [
            "✦  Runs locally on your Mac",
            "✦  Integrates with your existing TradingView setup",
            "✦  Zero data sent to third-party servers",
        ],
        "accent":  ACCENT1,
        "glow_l":  (ACCENT2, 180, 880),
        "glow_r":  (ACCENT1, 840, 200),
        "chart":   False,
    },
    {
        "badge":   "🔄  WORKFLOW  |  NEURAL-ENGINE",
        "number":  "03",
        "head":    "Step 2: Signals Overlay\nYour Charts.",
        "sub":     "You analyze. You decide. The AI just highlights.",
        "bullets": [
            "✦  Pattern signals surface in real time",
            "✦  Overlay is non-intrusive — your chart stays yours",
            "✦  No black box — you see exactly what triggered",
        ],
        "accent":  GOLD,
        "glow_l":  (ACCENT1, 200, 200),
        "glow_r":  (ACCENT2, 820, 820),
        "chart":   False,
    },
    {
        "badge":   "🔄  WORKFLOW  |  NEURAL-ENGINE",
        "number":  "04",
        "head":    "Step 3: You Trade.\n100% Your Call.",
        "sub":     "Neural-Engine supports. You stay in control.",
        "bullets": [
            "✦  No auto-trading, ever",
            "✦  Review the signal — take it or leave it",
            "✦  Your broker, your rules, your risk",
        ],
        "accent":  ACCENT2,
        "glow_l":  (ACCENT2, 200, 880),
        "glow_r":  (ACCENT1, 820, 160),
        "chart":   False,
        "cta":     True,
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def draw_gradient(img):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def draw_grid(draw):
    for x in range(0, W, 64):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
    for y in range(0, H, 64):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)

def glow_circle(draw, cx, cy, r, color, steps=8):
    for i in range(steps, 0, -1):
        radius = r + (steps - i) * 7
        alpha  = int(55 * (i / steps))
        box = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(box, fill=(*color[:3], alpha))

def load_font(size, bold=False):
    candidates = [
        f"/System/Library/Fonts/{'SFProDisplay-Bold' if bold else 'SFProDisplay-Regular'}.otf",
        f"/System/Library/Fonts/{'SFProText-Bold' if bold else 'SFProText-Regular'}.otf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def text_width(font, text):
    bb = font.getbbox(text)
    return bb[2] - bb[0]

def text_height(font, text):
    bb = font.getbbox(text)
    return bb[3] - bb[1]

def draw_centered(draw, text, y, font, fill, max_w=904):
    """Draw text centered, wrapping if needed."""
    words = text.split()
    lines = []
    line  = ""
    for w in words:
        test = (line + " " + w).strip()
        if text_width(font, test) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    line_h = text_height(font, "Ag") + 8
    total_h = len(lines) * line_h
    cur_y   = y
    for ln in lines:
        x = (W - text_width(font, ln)) // 2
        draw.text((x, cur_y), ln, font=font, fill=fill)
        cur_y += line_h
    return cur_y  # return bottom y

def draw_chart_motif(draw):
    """Subtle candlestick / line chart in background (right side)."""
    bars = [
        (680, 580, 680, 460, 680, 430, 680, 610),  # x_open,y_open,x_close,y_close,x_top,y_top,x_bot,y_bot
        (730, 500, 730, 410, 730, 385, 730, 530),
        (780, 420, 780, 510, 780, 395, 780, 540),
        (830, 380, 830, 290, 830, 270, 830, 410),
        (880, 310, 880, 200, 880, 180, 880, 335),
    ]
    # Draw as simple vertical bars with caps
    for i, (x, yo, xc, yc, xt, yt, xb, yb) in enumerate(bars):
        alpha = 25 + i * 8
        col   = (*ACCENT1[:3], alpha)
        # wick
        draw.line([(x, yt), (x, yb)], fill=col, width=2)
        # body
        body_top = min(yo, yc)
        body_bot = max(yo, yc)
        for px in range(x - 8, x + 9):
            draw.line([(px, body_top), (px, body_bot)], fill=col, width=1)

def draw_step_number(draw, num_str, accent):
    """Big faint step number in the background."""
    big_font = load_font(320, bold=True)
    col = (*accent[:3], 18)
    x = W - text_width(big_font, num_str) - 30
    y = H // 2 - 160
    draw.text((x, y), num_str, font=big_font, fill=col)

# ── Render each slide ─────────────────────────────────────────────────────────
os.makedirs(f"assets/ig", exist_ok=True)

for idx, slide in enumerate(SLIDES, start=1):
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw_gradient(img)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    draw_grid(od)
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Background glows
    gl_color, gl_x, gl_y = slide["glow_l"]
    gr_color, gr_x, gr_y = slide["glow_r"]
    glow_circle(draw, gl_x, gl_y, 90, gl_color, steps=10)
    glow_circle(draw, gr_x, gr_y, 70, gr_color, steps=8)

    # Optional chart motif (slide 1)
    if slide.get("chart"):
        draw_chart_motif(draw)

    # Faint step number
    if slide["number"] != "01":
        draw_step_number(draw, slide["number"], slide["accent"])

    accent = slide["accent"]

    # ── Badge ──────────────────────────────────────────────────────────────────
    badge_font = load_font(20, bold=True)
    bt = slide["badge"]
    bw = text_width(badge_font, bt) + 36
    bh = 36
    bx = (W - bw) // 2
    draw.rounded_rectangle([bx, 52, bx + bw, 52 + bh],
                            radius=18, fill=(*accent[:3], 180))
    draw.text(((W - text_width(badge_font, bt)) // 2, 60),
              bt, font=badge_font, fill=WHITE)

    # ── Slide number pill (top-left) ───────────────────────────────────────────
    num_font = load_font(18, bold=True)
    num_label = f"  {slide['number']} / 04  "
    nw = text_width(num_font, num_label) + 4
    draw.rounded_rectangle([48, 52, 48 + nw, 52 + 30],
                            radius=15, fill=(*DARK_CARD,))
    draw.text((52, 57), num_label, font=num_font, fill=GREY)

    # ── Accent divider under badge ─────────────────────────────────────────────
    div_y = 100
    draw.line([(W // 2 - 60, div_y), (W // 2 + 60, div_y)],
              fill=(*accent[:3], 160), width=2)

    # ── Headline ───────────────────────────────────────────────────────────────
    head_font  = load_font(62, bold=True)
    head_lines = slide["head"].split("\n")
    head_y     = 124
    for hl in head_lines:
        x = (W - text_width(head_font, hl)) // 2
        draw.text((x, head_y), hl, font=head_font, fill=WHITE)
        head_y += text_height(head_font, hl) + 6

    # ── Subheadline ────────────────────────────────────────────────────────────
    sub_font = load_font(28)
    sub_y    = head_y + 18
    draw.text(((W - text_width(sub_font, slide["sub"])) // 2, sub_y),
              slide["sub"], font=sub_font, fill=GREY)
    cur_y = sub_y + text_height(sub_font, slide["sub"]) + 48

    # ── Bullets (if any) ───────────────────────────────────────────────────────
    if slide["bullets"]:
        b_font = load_font(30, bold=False)
        card_pad = 36
        card_h_total = len(slide["bullets"]) * 72 + card_pad
        draw.rounded_rectangle(
            [60, cur_y, W - 60, cur_y + card_h_total],
            radius=18,
            fill=(*DARK_CARD,),
            outline=(*accent[:3], 60),
            width=1,
        )
        b_y = cur_y + card_pad // 2 + 8
        for bullet in slide["bullets"]:
            draw.text((100, b_y), bullet, font=b_font, fill=WHITE)
            b_y += 72
        cur_y += card_h_total + 32

    # ── CTA strip (last slide) ─────────────────────────────────────────────────
    if slide.get("cta"):
        cta_y = cur_y + 12
        draw.rounded_rectangle([60, cta_y, W - 60, cta_y + 72],
                                radius=16,
                                fill=(*ACCENT1[:3], 28),
                                outline=(*ACCENT1[:3], 110),
                                width=2)
        cta_font = load_font(29, bold=True)
        cta_text = "Join the Waitlist  →  neural-engine.ai"
        draw.text(((W - text_width(cta_font, cta_text)) // 2, cta_y + 18),
                  cta_text, font=cta_font, fill=ACCENT1)

    # ── Footer ─────────────────────────────────────────────────────────────────
    footer_font = load_font(22, bold=True)
    disc_font   = load_font(17)
    brand_y     = H - 88
    draw.line([(60, brand_y - 14), (W - 60, brand_y - 14)],
              fill=(*ACCENT2[:3], 80), width=1)
    draw.text((60, brand_y), "NEURAL-ENGINE", font=footer_font, fill=ACCENT1)
    disc_text = "Not financial advice. Trade responsibly."
    draw.text((W - text_width(disc_font, disc_text) - 60, brand_y + 4),
              disc_text, font=disc_font, fill=GREY)

    # ── Save ───────────────────────────────────────────────────────────────────
    out = f"assets/ig/{DATE}-AM-{SLUG}-S{idx:02d}.png"
    img.convert("RGB").save(out, "PNG")
    print(f"Saved: {out}")

print("Done.")
