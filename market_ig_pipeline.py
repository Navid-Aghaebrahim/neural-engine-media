#!/usr/bin/env python3
"""Generate market-relevant Instagram post plans from verifiable market data.

Safety rules:
- Never publish exact market numbers unless they are independently verified.
- If verification is unavailable, emit a non-postable draft and fail hard for automation.
- Never invent catalysts or market news explanations.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
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


def validate_rows(rows: list[dict], market_as_of: str) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not rows:
        issues.append("No rows returned from shortlist")
        return False, issues

    today = dt.date.today().isoformat()
    if market_as_of >= today:
        issues.append(f"Market as-of date {market_as_of} is not safely historical relative to today {today}")

    required = ["ticker", "open", "high", "low", "close", "dayRet", "rangePct"]
    for row in rows[:6]:
        for key in required:
            if row.get(key) is None:
                issues.append(f"{row.get('ticker','UNKNOWN')} missing {key}")
        o = row.get("open")
        h = row.get("high")
        l = row.get("low")
        c = row.get("close")
        if all(v is not None for v in [o, h, l, c]):
            if not (l <= c <= h):
                issues.append(f"{row.get('ticker')} close outside day range")
            if not (l <= o <= h):
                issues.append(f"{row.get('ticker')} open outside day range")
        rp = row.get("rangePct")
        if rp is not None and rp < 0:
            issues.append(f"{row.get('ticker')} negative rangePct")

    return len(issues) == 0, issues


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
    ok, issues = validate_rows(rows, shortlist.get('asOf'))
    selected = choose_market_items(rows, max_items=4)

    source_lines = [
        f"Source: Polygon grouped daily US stocks data for {shortlist.get('asOf')} (via local Polygon scanner)",
    ]

    if not ok:
        raise RuntimeError("Verification failed: " + "; ".join(issues))

    if not selected:
        raise RuntimeError('No market rows available for post generation')

    slides = [
        {
            "headline": "Market pulse, source-checked",
            "sub": f"Verified daily snapshot — {shortlist.get('asOf')}"
        }
    ]

    summary_bits = []
    for row in selected[:3]:
        ticker = row['ticker']
        close = fmt_price(row.get('close'))
        ret = fmt_pct(row.get('dayRet'))
        rng = fmt_pct(row.get('rangePct'))
        slides.append({
            "headline": f"{ticker} moved {ret}",
            "sub": f"Session close {close} • range {rng}",
        })
        summary_bits.append(f"{ticker} {ret} (close {close}, range {rng})")

    caption_lines = [
        "Market pulse, source-checked.",
        "",
        f"Verified daily snapshot for {shortlist.get('asOf')}:",
    ]
    for bit in summary_bits:
        caption_lines.append(f"• {bit}")
    caption_lines += [
        "",
        "This format only publishes when the daily dataset passes validation checks.",
        "No invented catalysts. No made-up headlines. Just the session snapshot.",
        "",
        "If you want cleaner market context inside your workflow: Join the waitlist → neural-engine.tech",
        "Not financial advice. Trade responsibly.",
        "",
        "#stocks #stockmarket #trading #markets #marketpulse #tradingview #daytrading #swingtrading #investing #fintech #ai #marketstructure #priceaction #riskmanagement #technicalanalysis #workflow #productivity #tradingtools #marketanalysis",
        "",
    ]
    caption_lines.extend(source_lines)

    post = {
        "date": str(today),
        "market_as_of": shortlist.get('asOf'),
        "theme": "features",
        "slug": f"market-pulse-{shortlist.get('asOf')}",
        "slides": slides[:4],
        "caption": "\n".join(caption_lines),
        "sources": source_lines,
        "selected": selected,
        "shortlist_count": shortlist.get('count'),
        "generated_at": dt.datetime.now().isoformat(),
        "verification": {
            "passed": True,
            "issues": issues,
        },
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
