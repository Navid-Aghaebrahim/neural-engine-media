#!/usr/bin/env python3
"""
Neural-Engine IG Single — 2026-02-25 PM
Theme: FAQ — "How does Neural-Engine actually work?"
"""

import os, sys, textwrap, math
from PIL import Image, ImageDraw, ImageFont

OUT_PATH = "assets/ig/2026-02-25-PM-faq-how-it-works.png"
W, H = 1024, 1024

# ── Colours ──────────────────────────────────────────────────────────────────
BG_TOP    = (8,  10,  22)       # deep navy
BG_BOT    = (14, 20,  48)
ACCENT1   = (94, 234, 212)      # teal
ACCENT2   = (139, 92, 246)      # violet
GOLD      = (251, 191, 36)
WHITE     = (255, 255, 255)
GREY      = (160, 170, 200)
DARK_CARD = (18, 24, 52)

def draw_gradient(img):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0]-BG_TOP[0])*t)
        g = int(BG_TOP[1] + (BG_BOT[1]-BG_TOP[1])*t)
        b = int(BG_TOP[2] + (BG_BOT[2]-BG_TOP[2])*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))

def draw_grid(draw):
    for x in range(0, W, 64):
        draw.line([(x,0),(x,H)], fill=(255,255,255,12), width=1)
    for y in range(0, H, 64):
        draw.line([(0,y),(W,y)], fill=(255,255,255,12), width=1)

def glow_circle(draw, cx, cy, r, color, steps=8):
    for i in range(steps, 0, -1):
        alpha = int(60 * (i / steps))
        radius = r + (steps - i) * 6
        box = [cx-radius, cy-radius, cx+radius, cy+radius]
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
            except:
                pass
    return ImageFont.load_default()

def centered_text(draw, text, y, font, fill, max_w=900, line_spacing=8):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    lh = font.getbbox("Ag")[3] - font.getbbox("Ag")[1] + line_spacing
    for i, line in enumerate(lines):
        bx = font.getbbox(line)
        lw = bx[2] - bx[0]
        draw.text(((W - lw)//2, y + i*lh), line, font=font, fill=fill)
    return y + len(lines)*lh

# ── FAQ rows ─────────────────────────────────────────────────────────────────
FAQS = [
    ("Does it send my data anywhere?",
     "No. Everything runs on your Mac. Zero cloud."),
    ("Do I need to leave TradingView?",
     "Never. The overlay lives inside TradingView."),
    ("Does it trade for me?",
     "No — it flags setups. You pull the trigger."),
]

def draw_faq_card(draw, x, y, w, h, q, a, q_font, a_font):
    # card bg
    draw.rounded_rectangle([x, y, x+w, y+h], radius=18,
                            fill=(*DARK_CARD, 230),
                            outline=(*ACCENT2[:3], 80), width=1)
    # Q marker
    qm_font = load_font(20, bold=True)
    draw.text((x+20, y+18), "Q", font=qm_font, fill=GOLD)
    draw.text((x+20, y+18+26), "A", font=qm_font, fill=ACCENT1)

    # Question
    qx = x + 52
    qy = y + 16
    q_bbox = q_font.getbbox(q)
    draw.text((qx, qy), q, font=q_font, fill=WHITE)

    # Answer
    ay = qy + (q_bbox[3]-q_bbox[1]) + 8
    draw.text((qx, ay), a, font=a_font, fill=ACCENT1)

img = Image.new("RGBA", (W, H), (0,0,0,255))
draw_gradient(img)

overlay = Image.new("RGBA", (W, H), (0,0,0,0))
od = ImageDraw.Draw(overlay)
draw_grid(od)
img = Image.alpha_composite(img, overlay)

draw = ImageDraw.Draw(img)

# decorative glows
glow_circle(draw, 820, 160, 80, ACCENT2, steps=10)
glow_circle(draw, 200, 880, 60, ACCENT1, steps=8)

# ── Badge ─────────────────────────────────────────────────────────────────────
badge_font = load_font(20, bold=True)
badge_text = "❓  FAQ  |  NEURAL-ENGINE"
bx = badge_font.getbbox(badge_text)
bw = bx[2]-bx[0]+36; bh = 36
draw.rounded_rectangle([(W-bw)//2-2, 52, (W+bw)//2+2, 52+bh],
                        radius=18, fill=(*ACCENT2[:3], 180))
draw.text(((W - (bx[2]-bx[0]))//2, 60), badge_text, font=badge_font, fill=WHITE)

# ── Headline ──────────────────────────────────────────────────────────────────
h1_font = load_font(68, bold=True)
h1 = "How Does It Work?"
bx = h1_font.getbbox(h1)
draw.text(((W-(bx[2]-bx[0]))//2, 110), h1, font=h1_font, fill=WHITE)

# ── Subheadline ───────────────────────────────────────────────────────────────
sub_font = load_font(28)
sub_y = 110 + (bx[3]-bx[1]) + 12
sub = "Real questions. Straight answers."
sbx = sub_font.getbbox(sub)
draw.text(((W-(sbx[2]-sbx[0]))//2, sub_y), sub, font=sub_font, fill=GREY)

# ── FAQ Cards ─────────────────────────────────────────────────────────────────
q_font = load_font(26, bold=True)
a_font = load_font(24)
card_y = sub_y + 55
card_h = 110
gap = 24

for q_text, a_text in FAQS:
    draw_faq_card(draw, 60, card_y, W-120, card_h, q_text, a_text, q_font, a_font)
    card_y += card_h + gap

# ── CTA strip ─────────────────────────────────────────────────────────────────
cta_y = card_y + 24
draw.rounded_rectangle([60, cta_y, W-60, cta_y+72], radius=16,
                        fill=(*ACCENT1[:3], 30),
                        outline=(*ACCENT1[:3], 120), width=2)
cta_font = load_font(30, bold=True)
cta_text = "Join the Waitlist  →  neural-engine.ai"
ctax = cta_font.getbbox(cta_text)
draw.text(((W-(ctax[2]-ctax[0]))//2, cta_y+18), cta_text, font=cta_font, fill=ACCENT1)

# ── Footer logo / brand ────────────────────────────────────────────────────────
footer_font = load_font(22, bold=True)
disc_font   = load_font(17)

brand_y = H - 88
draw.text((60, brand_y), "NEURAL-ENGINE", font=footer_font, fill=ACCENT1)
disc_text = "Not financial advice. Trade responsibly."
dbx = disc_font.getbbox(disc_text)
draw.text((W-(dbx[2]-dbx[0])-60, brand_y+4), disc_text, font=disc_font, fill=GREY)

# thin separator line
draw.line([(60, brand_y-14),(W-60, brand_y-14)], fill=(*ACCENT2[:3], 80), width=1)

img = img.convert("RGB")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
img.save(OUT_PATH, "PNG")
print(f"Saved: {OUT_PATH}")
