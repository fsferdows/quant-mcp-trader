---
name: freqtrade-strategy-lab
description: >-
  Author, validate, backtest, hyperopt, and audit Freqtrade trading strategies
  for lookahead and recursive bias using local historical OHLCV data. Use when
  developing, tuning, or comparing Freqtrade strategies in user_data/strategies/.
---

# Freqtrade Strategy Lab

Use this workflow whenever creating, modifying, or evaluating a strategy in `user_data/strategies/` or adapting patterns from `external_strategies/freqtrade-strategies/`.

## 1. Validate Strategy Discovery
Confirm the strategy loads cleanly without syntax errors or duplicate names:
```bash
./.venv/bin/freqtrade list-strategies -c config.json
```

## 2. Refresh Historical Data
Ensure the local data cache matches the strategy's `timeframe` and any `informative_pairs()` timeframes:
```bash
./.venv/bin/freqtrade download-data \
  --config config.json \
  --timeframe 5m 15m 1h 4h 1d \
  --days 90
```

## 3. Run Backtesting
Evaluate win rate, profit factor, Sharpe/Sortino ratio, max drawdown, and trade count:
```bash
./.venv/bin/freqtrade backtesting \
  --config config.json \
  --strategy <StrategyName> \
  --timeframe 5m \
  --timerange 20260824- \
  --enable-protections \
  --cache none
```
Compare multiple strategies side by side using `--strategy-list <StratA> <StratB>`.

## 4. Audit for Bias (Mandatory Before Paper Trading)
Check that the strategy does not leak future candle data (`lookahead-analysis`) or suffer from unstable indicator warm-up (`recursive-analysis`):
```bash
./.venv/bin/freqtrade lookahead-analysis \
  --config config.json \
  --strategy <StrategyName> \
  --timerange 20260824-

./.venv/bin/freqtrade recursive-analysis \
  --config config.json \
  --strategy <StrategyName> \
  --timerange 20260824-
```

## 5. Hyperparameter Optimization (Optional)
Optimize bounded parameter spaces (`buy`, `sell`, `roi`, `stoploss`, `trailing`) using Sharpe-based loss and avoid overfitting by validating out-of-sample:
```bash
./.venv/bin/freqtrade hyperopt \
  --config config.json \
  --strategy <StrategyName> \
  --hyperopt-loss SharpeHyperOptLossDaily \
  --epochs 200 \
  --spaces buy sell \
  --min-trades 30
```
