---
name: freqtrade-live-operations
description: >-
  Start, monitor, inspect, and manage the real-time Freqtrade paper-trading bot
  via CLI, FreqUI (http://127.0.0.1:8080), and freqtrade-mcp tools. Use when
  operating or troubleshooting the live dry-run bot.
---

# Freqtrade Live Operations (Paper Trading)

## 1. Start Real-Time Paper Trading Bot
Launch Freqtrade in `dry_run` mode with REST API + FreqUI enabled at `http://127.0.0.1:8080`:
```bash
./run_paper_trade.sh
```
Default local credentials in `config.json`:
- URL: `http://127.0.0.1:8080`
- Username / Password: `freqtrader` / `freqtrader`

## 2. Verify Bot Health & Telemetry via `freqtrade-mcp`
When `freqtrade-mcp` is connected:
- `ping_bot` — Confirm API connectivity (`{"status": "pong"}`)
- `fetch_config` — Confirm `"dry_run": true`, active strategy, and stake limits
- `fetch_balance` — Inspect simulated USDT wallet and locked capital
- `fetch_bot_status` — Inspect currently open paper trades and unrealized P&L
- `fetch_profit` / `fetch_daily_profit` / `fetch_performance` — Review realized returns and per-pair breakdown
- `fetch_logs` — Inspect recent strategy / order logs

## 3. Safe Runtime Controls
- `stop_buy` — Pause new entries while letting open trades exit cleanly
- `reload_config` — Apply config or strategy changes safely
- `add_blacklist` / `delete_blacklist` — Temporarily exclude illiquid or anomalous pairs
- `stop_bot` / `start_bot` — Pause or resume the trading loop

## 4. Direct REST API Check (Fallback)
```bash
curl -s -u freqtrader:freqtrader http://127.0.0.1:8080/api/v1/ping
```
