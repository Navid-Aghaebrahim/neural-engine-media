#!/usr/bin/env python3
"""
Neural-Engine IG Single — 2026-02-26 PM
Theme: Social Proof — community momentum / waitlist growing
"""

import os, math
from PIL import Image, ImageDraw, ImageFont

OUT_PATH = "assets/ig/2026-02-26-PM-social-proof-community.png"
W, H = 1024, 1024

# ── Colours ──────────────────────────────────────────────────────────────────
BG_TOP    = (6,  8,  20)
BG_BOT    = (12, 18, 44)
ACCENT1   = (94, 234, 212)      # teal
ACCENT2   = (139, 92, 246)      # violet
GOLD      = (251, 191, 36)
WHITE     = (255, 255, 255)
GREY      = (160, 170, 200)
DARK_CARD = (16, 22, 50)

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
        draw.line([(x,0),(x,H)], fill=(255,255,255,10), width=1)
    for y in range(0, H, 64):
        draw.line([(0,y),(W,y)], fill=(255,255,255,10), width=1)

def glow_circle(draw, cx, cy, r, color, steps=8):
    for i in range(steps, 0, -1):
        alpha = int(55 * (i / steps))
        radius = r + (steps - i) * 7
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

def wrap_text(text, font, max_w):
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
    return lines

def draw_centered(draw, text, y, font, fill, max_w=900, line_spacing=10):
    lines = wrap_text(text, font, max_w)
    lh = font.getbbox("Ag")[3] - font.getbbox("Ag")[1] + line_spacing
    for i, line in enumerate(lines):
        bx = font.getbbox(line)
        lw = bx[2] - bx[0]
        draw.text(((W - lw) // 2, y + i * lh), line, font=font, fill=fill)
    return y + len(lines) * lh

# ── Quote cards ──────────────────────────────────────────────────────────────
QUOTES = [
    ("Finally — AI signals I can actually understand.",  "Beta tester, Options trader"),
    ("Love that it lives inside TradingView. Zero friction.", "Beta tester, Swing trader"),
    ("It flags the setup. I make the call. That's the deal.", "Early access member"),
]

def draw_quote_card(draw, x, y, w, h, quote, author, q_font, a_font):
    # card background
    draw.rounded_rectangle(
        [x, y, x+w, y+h], radius=20,
        fill=(*DARK_CARD, 220),
        outline=(*ACCENT1[:3], 70), width=1
    )
    # opening quotation mark
    qm_font = load_font(52, bold=True)
    draw.text((x+20, y+6), "\u201c", font=qm_font, fill=(*GOLD, 200))

    # quote text
    q_lines = wrap_text(quote, q_font, w - 80)
    lh = q_font.getbbox("Ag")[3] - q_font.getbbox("Ag")[1] + 6
    qy = y + 44
    for line in q_lines:
        draw.text((x + 60, qy), line, font=q_font, fill=WHITE)
        qy += lh

    # author
    draw.text((x + 60, qy + 6), f"— {author}", font=a_font, fill=ACCENT1)


# ── Build image ───────────────────────────────────────────────────────────────
img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
draw_gradient(img)

overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
draw_grid(od)
img = Image.alpha_composite(img, overlay)

draw = ImageDraw.Draw(img)

# decorative glows
glow_circle(draw, 860, 140, 90, ACCENT2, steps=10)
glow_circle(draw, 160, 900, 70, ACCENT1, steps=8)
glow_circle(draw, 512, 512, 200, ACCENT2, steps=6)   # subtle center glow

# ── Top badge ─────────────────────────────────────────────────────────────────
badge_font = load_font(19, bold=True)
badge_text = "🗣  COMMUNITY  |  NEURAL-ENGINE"
bx = badge_font.getbbox(badge_text)
bw = bx[2] - bx[0] + 36; bh = 36
draw.rounded_rectangle(
    [(W - bw)//2 - 2, 48, (W + bw)//2 + 2, 48 + bh],
    radius=18, fill=(*ACCENT1[:3], 35), outline=(*ACCENT1[:3], 120), width=1
)
draw.text(((W - (bx[2]-bx[0]))//2, 56), badge_text, font=badge_font, fill=ACCENT1)

# ── Headline ──────────────────────────────────────────────────────────────────
h1_font = load_font(62, bold=True)
h1 = "The Waitlist Is Talking."
bx = h1_font.getbbox(h1)
draw.text(((W - (bx[2]-bx[0]))//2, 104), h1, font=h1_font, fill=WHITE)

# ── Subheadline ───────────────────────────────────────────────────────────────
sub_font = load_font(27)
sub_y = 104 + (h1_font.getbbox(h1)[3] - h1_font.getbbox(h1)[1]) + 10
sub = "Here's what early testers are saying."
sbx = sub_font.getbbox(sub)
draw.text(((W - (sbx[2] - sbx[0]))//2, sub_y), sub, font=sub_font, fill=GREY)

# ── Quote Cards ───────────────────────────────────────────────────────────────
q_font  = load_font(24, bold=False)
a_font  = load_font(20, bold=True)
card_y  = sub_y + 48
card_h  = 118
gap     = 20

for quote, author in QUOTES:
    draw_quote_card(draw, 52, card_y, W - 104, card_h, quote, author, q_font, a_font)
    card_y += card_h + gap

# ── Momentum counter strip ────────────────────────────────────────────────────
counter_y = card_y + 20
draw.rounded_rectangle(
    [52, counter_y, W - 52, counter_y + 68],
    radius=16, fill=(*ACCENT2[:3], 25),
    outline=(*ACCENT2[:3], 110), width=2
)
ctr_font = load_font(28, bold=True)
ctr_text = "🚀  Waitlist growing fast — spots are limited"
ctx = ctr_font.getbbox(ctr_text)
draw.text(((W - (ctx[2]-ctx[0]))//2, counter_y + 18), ctr_text, font=ctr_font, fill=GOLD)

# ── CTA ───────────────────────────────────────────────────────────────────────
cta_y = counter_y + 68 + 20
draw.rounded_rectangle(
    [52, cta_y, W - 52, cta_y + 68],
    radius=16, fill=(*ACCENT1[:3], 28),
    outline=(*ACCENT1[:3], 130), width=2
)
cta_font  = load_font(29, bold=True)
cta_text  = "Join the Waitlist  →  neural-engine.ai"
ctx = cta_font.getbbox(cta_text)
draw.text(((W - (ctx[2]-ctx[0]))//2, cta_y + 18), cta_text, font=cta_font, fill=ACCENT1)

# ── Footer ────────────────────────────────────────────────────────────────────
footer_font = load_font(21, bold=True)
disc_font   = load_font(16)

brand_y = H - 80
draw.line([(52, brand_y - 14), (W - 52, brand_y - 14)], fill=(*ACCENT2[:3], 80), width=1)
draw.text((52, brand_y), "NEURAL-ENGINE", font=footer_font, fill=ACCENT1)
disc_text = "Not financial advice. Trade responsibly."
dbx = disc_font.getbbox(disc_text)
draw.text((W - (dbx[2]-dbx[0]) - 52, brand_y + 4), disc_text, font=disc_font, fill=GREY)

# ── Save ──────────────────────────────────────────────────────────────────────
img = img.convert("RGB")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
img.save(OUT_PATH, "PNG")
print(f"Saved: {OUT_PATH}")
