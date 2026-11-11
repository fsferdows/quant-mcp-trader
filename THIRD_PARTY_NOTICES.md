# Third-Party Notices

This workspace integrates and builds upon the following open-source projects:

1. **Freqtrade** (`https://github.com/freqtrade/freqtrade`) — GPL-3.0 License
   - Cloned during setup into `freqtrade/`.
2. **Freqtrade Strategies** (`https://github.com/freqtrade/freqtrade-strategies`) — GPL-3.0 / Strategy-specific Licenses
   - Cloned during setup into `external_strategies/freqtrade-strategies/`.
   - `user_data/strategies/UniversalMACDSafe.py` adapts `UniversalMACD` by Masoud Azizi (`@mablue`) with 200-candle warmup, `-8%` hard stoploss, `exit_profit_only`, and Freqtrade protections.
3. **kukapay/freqtrade-mcp** (`https://github.com/kukapay/freqtrade-mcp`) — MIT License, Copyright (c) 2025 kukapay
   - Vendored in `mcp_servers/freqtrade-mcp/` with compatibility updates for `mcp >= 1.5,<2` and `freqtrade-client >= 2026.x`.
4. **kukapay/crypto-indicators-mcp** (`https://github.com/kukapay/crypto-indicators-mcp`) — MIT License, Copyright (c) 2025 kukapay
   - Located in `mcp_servers/crypto-indicators-mcp/`.
5. **kukapay/crypto-feargreed-mcp** (`https://github.com/kukapay/crypto-feargreed-mcp`) — MIT License, Copyright (c) 2025 kukapay
   - Located in `mcp_servers/crypto-feargreed-mcp/` with async `ctx.info` compatibility fix.
6. **ccxt-mcp** (`https://github.com/ccxt/ccxt/tree/master/mcp`) — MIT License, Copyright (c) CCXT
   - Installed via npm inside `mcp_servers/ccxt-mcp/`.
