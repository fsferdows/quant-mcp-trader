# Freqtrade Trading Workspace Rules

1. **Dry-Run / Paper Trading Default**: Never enable live trading (`dry_run: false`) or add real exchange API keys without explicit user confirmation and documented backtest + paper-trading validation.
2. **No Impossible Guarantees**: Never claim a 100% win rate or risk-free trading. Always report honest backtest drawdowns, win rates, profit factor, Sharpe/Sortino ratios, and trade counts.
3. **Mandatory Verification Before Deployment**: Every strategy edit must be validated with:
   - `freqtrade list-strategies -c config.json`
   - `freqtrade backtesting -c config.json --strategy <Name>`
   - `freqtrade lookahead-analysis -c config.json --strategy <Name>`
   - `freqtrade recursive-analysis -c config.json --strategy <Name>`
4. **Supported Exchanges Only**: Freqtrade supports cryptocurrency exchanges via CCXT (Binance, OKX, Bybit, Kraken, etc.), NOT binary options platforms such as Pocket Option.
5. **Risk Controls**: Every strategy must define explicit `stoploss`, position protections (`StoplossGuard`, `MaxDrawdown`, `CooldownPeriod`), and realistic `stake_amount` / `max_open_trades`.
