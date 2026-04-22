#!/usr/bin/env python3
"""Generate market-relevant Instagram post plans from real Polygon data.

Outputs:
- tmp/market_ig_post.json   -> structured post plan + sources
- tmp/market_ig_caption.txt -> caption with explicit source lines
- tmp/market_ig_content.json -> carousel slides for gen_ig_carousel_daily_fal.py

Design:
- Use real market data from Polygon via the existing trading scanner module.
- Focus on liquid/significant names like SPY / NVDA / TSLA when present, plus other top movers from shortlist.
- Never invent news headlines.
- Cite the source and as-of date in the copy payload.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
TRADING = WORKSPACE / "ne_remote_stock_trading"
if str(TRADING) not in sys.path:
    sys.path.insert(0, str(TRADING))

from polygon_scan import build_shortlist  # type: ignore

TMP = ROOT / "tmp"
TMP.mkdir(parents=True, exist_ok=True)

TRACKED = ["SPY", "QQQ", "NVDA", "TSLA", "AAPL", "MSFT", "META", "AMZN", "GOOGL", "GLD"]


def fmt_pct(x: float | None) -> str:
    if x is None:
        return "n/a"
    return f"{x * 100:+.2f}%"


def fmt_price(x: float | None) -> str:
    if x is None:
        return "n/a"
    return f"${x:,.2f}"


def choose_market_items(rows: list[dict], max_items: int = 4) -> list[dict]:
    by_ticker = {r.get('ticker'): r for r in rows}
    picked: list[dict] = []

    for ticker in TRACKED:
        row = by_ticker.get(ticker)
        if row and row not in picked:
            picked.append(row)
        if len(picked) >= max_items:
            return picked

    ranked = sorted(rows, key=lambda r: abs(float(r.get('dayRet') or 0.0)), reverse=True)
    for row in ranked:
        if row not in picked:
            picked.append(row)
        if len(picked) >= max_items:
            break
    return picked


def build_post(date_str: str | None = None) -> dict:
    today = dt.date.today()
    if date_str:
        market_date = dt.date.fromisoformat(date_str)
    else:
        market_date = today - dt.timedelta(days=1)
        while market_date.weekday() >= 5:
            market_date -= dt.timedelta(days=1)

    shortlist = build_shortlist(market_date, 100_000_000.0, 150)

    rows = shortlist.get('rows') or []
    selected = choose_market_items(rows, max_items=4)
    if not selected:
        raise RuntimeError('No market rows available for post generation')

    slides = []
    summary_bits = []
    source_lines = [
        f"Source: Polygon grouped daily US stocks data for {shortlist.get('asOf')} (via local Polygon scanner)",
    ]

    slides.append({
        "headline": "What actually moved the tape?",
        "sub": f"Real market data snapshot — {shortlist.get('asOf')}"
    })

    for row in selected[:3]:
        ticker = row['ticker']
        close = fmt_price(row.get('close'))
        ret = fmt_pct(row.get('dayRet'))
        rng = fmt_pct(row.get('rangePct'))
        slides.append({
            "headline": f"{ticker} closed {ret}",
            "sub": f"Close {close} • intraday range {rng}",
        })
        summary_bits.append(f"{ticker} {ret} (close {close}, range {rng})")

    if len(slides) < 4:
        last = selected[-1]
        slides.append({
            "headline": f"{last['ticker']} stayed active",
            "sub": f"Close {fmt_price(last.get('close'))} • range {fmt_pct(last.get('rangePct'))}",
        })

    title = "Market pulse without the noise"
    caption_lines = [
        f"{title}.",
        "",
        f"Real data snapshot for {shortlist.get('asOf')}:",
    ]
    for bit in summary_bits:
        caption_lines.append(f"• {bit}")
    caption_lines += [
        "",
        "The point is not to chase every move. It’s to notice where attention, volatility, and structure are actually showing up.",
        "",
        "If you want cleaner market context inside your workflow: Join the waitlist → neural-engine.tech",
        "Not financial advice. Trade responsibly.",
        "",
        "#stocks #stockmarket #trading #spy #nvidia #tesla #gold #markets #marketnews #tradingview #daytrading #swingtrading #investing #fintech #ai #marketstructure #priceaction #riskmanagement #stocktrader #wallstreet #macro #equities #volatility #technicalanalysis #tradingpsychology #workflow #productivity #fintechdesign #tradingtools #marketanalysis",
        "",
    ]
    caption_lines.extend(source_lines)

    post = {
        "date": str(today),
        "market_as_of": shortlist.get('asOf'),
        "theme": "features",
        "slug": f"market-pulse-{shortlist.get('asOf')}",
        "title": title,
        "slides": slides[:4],
        "caption": "\n".join(caption_lines),
        "sources": source_lines,
        "selected": selected,
        "shortlist_count": shortlist.get('count'),
        "generated_at": dt.datetime.now().isoformat(),
    }
    return post


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', default=None, help='Market date YYYY-MM-DD')
    args = ap.parse_args()

    post = build_post(args.date)
    (TMP / 'market_ig_post.json').write_text(json.dumps(post, indent=2) + '\n')
    (TMP / 'market_ig_caption.txt').write_text(post['caption'] + '\n')
    (TMP / 'market_ig_content.json').write_text(json.dumps(post['slides'], indent=2) + '\n')
    print(str(TMP / 'market_ig_post.json'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
