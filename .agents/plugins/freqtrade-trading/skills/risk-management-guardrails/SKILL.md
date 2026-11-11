---
name: risk-management-guardrails
description: >-
  Enforce capital-preservation rules, position sizing, stoploss design, and
  Freqtrade protections before running or modifying any trading strategy. Use
  when reviewing risk parameters or validating readiness for paper/live trading.
---

# Risk Management Guardrails

No trading strategy has a 100% win rate. Long-term survival depends on limiting drawdowns and cutting losing trades systematically.

## Mandatory Strategy & Config Checklist

1. **Dry-Run Verification**:
   - Confirm `"dry_run": true` in `config.json`.
   - Confirm `"force_entry_enable": false` unless explicitly testing manual entries.
2. **Hard Stoploss & Trailing Protection**:
   - Never run a strategy with `stoploss = -0.99` or missing stoploss.
   - Prefer volatility-appropriate stops (typically `-0.02` to `-0.08` on spot crypto) paired with trailing stop or `custom_stoploss`.
3. **Strategy-Level Protections (`protections`)**:
   - `CooldownPeriod`: Prevent rapid re-entry on the same pair right after a loss.
   - `StoplossGuard`: Pause trading temporarily after repeated stoploss hits.
   - `MaxDrawdown`: Halt entries if portfolio drawdown exceeds threshold (e.g., 10% over 24h).
4. **Position Sizing & Exposure**:
   - Limit `max_open_trades` (e.g. `3` to `5`) and keep `leverage` at `1.0` (`"trading_mode": "spot"`).
   - Filter illiquid pairs via `PrecisionFilter`, `PriceFilter`, `SpreadFilter`, and `AgeFilter`.
5. **Pre-Live Promotion Gate**:
   - Require positive profit factor (> 1.2), acceptable max drawdown (< 15%), zero lookahead bias, and at least 2–4 weeks of stable `dry_run` forward testing before considering any real funds.
