# Contributing

Contributions are welcome! Whether you want to submit a bias-audited Freqtrade strategy, improve an MCP server integration, or enhance the Agent Skills, thank you for helping improve this project.

## Pull Request Checklist

Before opening a pull request involving a strategy in `user_data/strategies/`:

1. **Strategy Discovery**:
   ```bash
   ./.venv/bin/freqtrade list-strategies -c config.json
   ```
2. **Backtesting with Protections**:
   ```bash
   ./.venv/bin/freqtrade backtesting -c config.json --strategy <StrategyName> --enable-protections --cache none
   ```
3. **Bias Audits (Mandatory)**:
   ```bash
   ./.venv/bin/freqtrade lookahead-analysis -c config.json --strategy <StrategyName>
   ./.venv/bin/freqtrade recursive-analysis -c config.json --strategy <StrategyName>
   ```
4. **Risk Controls**:
   - Keep `dry_run: true` and never commit API keys, secrets, or local `.sqlite` databases.
   - Include explicit `stoploss`, 1x spot leverage safety, and `protections` (`CooldownPeriod`, `StoplossGuard`, `MaxDrawdown`).
   - Report honest backtest metrics (win rate, drawdown, Sharpe/Sortino, profit factor, and trade count).
