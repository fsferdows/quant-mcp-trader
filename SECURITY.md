# Security Policy

## Safety Defaults

- This repository runs Freqtrade in **dry-run (paper trading)** mode by default (`"dry_run": true` in `config.example.json`).
- `config.json`, `.agents/plugins/freqtrade-trading/mcp_config.json`, `mcp_servers/ccxt-mcp/ccxt_config.json`, `.env`, and SQLite trade databases are excluded via `.gitignore`.
- Never commit exchange API keys, JWT secrets, or personal credentials.

## Reporting a Vulnerability

If you discover a security issue (such as credential exposure, unsafe MCP execution, or a bug in strategy risk controls), please contact **FS Ferdows** privately via `fsferdows@icloud.com` rather than opening a public issue with exploit details.
