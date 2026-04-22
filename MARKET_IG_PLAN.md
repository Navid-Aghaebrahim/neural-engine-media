# Market-Relevant Instagram Pipeline

## Goal
Use the existing Neural-Engine Instagram pipeline style, but generate posts tied to **real market conditions** using **actual Polygon data**.

## Rules
- No hallucinated headlines.
- No fabricated catalysts/news events.
- Only state facts available from the data source used.
- Every caption must include a **Source:** line.
- If later we add real news APIs (Reuters/WSJ/Alpha Vantage/Financial Modeling Prep/etc.), keep source attribution explicit per fact.

## Current data source
- Polygon grouped daily US stocks data via local scanner:
  - `/Users/navid/.openclaw/workspace/ne_remote_stock_trading/polygon_scan.py`
- Generator:
  - `market_ig_pipeline.py`

## Current content style
- Exciting but factual
- Focus on:
  - broad market proxies (SPY, QQQ)
  - major names (NVDA, TSLA, AAPL, MSFT, META, AMZN, GOOGL)
  - gold proxy (`GLD`) when present
- Avoid implying causation unless sourced from a real news feed

## Suggested posting slots
- 6:45 AM PT — premarket watchlist style (later, when premarket-capable data/news is wired in)
- 12:15 PM PT — midday pulse
- 4:30 PM PT — closing recap
- 8:30 PM PT — best-of-day educational recap

## Current safe implementation
Until a dedicated news API is added, use these as **market pulse / market recap** posts, not headline-news posts.
