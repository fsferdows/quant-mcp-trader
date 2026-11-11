---
name: realtime-market-analysis
description: >-
  Analyze live cryptocurrency prices, order books, technical indicators, and
  market sentiment in real time using ccxt-mcp, crypto-indicators-mcp,
  crypto-feargreed-mcp, and freqtrade-mcp. Use when evaluating market regime
  or reviewing live trading signals.
---

# Real-Time Market Analysis

Combine all connected market MCP servers before making strategy or operational recommendations.

## MCP Servers & Capabilities

1. **`ccxt-mcp`** — Real-time exchange market data (100+ exchanges, public endpoints without keys):
   - Live tickers & 24h volume (`get_tickers`)
   - Order book depth & bid/ask spread (`get_orderbook`)
   - Recent OHLCV candles (`get_ohlcv`) and market metadata (`search_markets`)
2. **`crypto-indicators-mcp`** — 50+ real-time technical indicators & strategy evaluators backed by Binance CCXT:
   - Trend: `calculate_exponential_moving_average`, `calculate_moving_average_convergence_divergence`, `calculate_parabolic_sar`, `calculate_vortex`
   - Momentum: `calculate_relative_strength_index`, `calculate_stochastic_oscillator`, `calculate_ichimoku_cloud`, `calculate_williams_r`
   - Volatility & Volume: `calculate_bollinger_bands`, `calculate_average_true_range`, `calculate_keltner_channel`, `calculate_chandelier_exit`
3. **`crypto-feargreed-mcp`** — Macro crypto market sentiment via Alternative.me:
   - `get_current_fng_tool` — Current Fear & Greed Index (0–100)
   - `analyze_fng_trend` — Multi-day sentiment trend and average
4. **`freqtrade-mcp`** — Live Freqtrade dry-run bot telemetry:
   - `fetch_market_data` — Strategy-analyzed candles with indicator columns
   - `fetch_bot_status` / `fetch_whitelist` — Active pairs and open positions

## Standard Market Briefing Workflow

1. Pull sentiment (`get_current_fng_tool`, `analyze_fng_trend(days=14)`).
2. Check BTC/USDT and ETH/USDT live prices, spreads, and liquidity via `ccxt-mcp` (`get_tickers`, `get_orderbook`).
3. Compute 15m/1h/4h trend and momentum via `crypto-indicators-mcp` (RSI, MACD, Bollinger Bands, ATR).
4. Cross-check against Freqtrade's analyzed dataframe (`fetch_market_data`) when the bot is running.
5. Summarize market regime (Trending Bull / Trending Bear / Ranging / High Volatility) and highlight risk posture.
