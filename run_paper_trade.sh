#!/bin/bash
# ============================================================
# Freqtrade Paper Trading Runner
# ============================================================
# Runs freqtrade in DRY RUN mode (paper trading).
# NO real money is used. Uses simulated $1000 USDT wallet.
#
# ⚠️ IMPORTANT: This is paper trading only!
# The config has dry_run=true. Do NOT change this without
# understanding the risks of real trading.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv
source "$SCRIPT_DIR/.venv/bin/activate" 2>/dev/null || {
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
}

echo "============================================"
echo "  🚀 Starting Freqtrade Paper Trading"
echo "============================================"
echo ""
echo "  Mode:     DRY RUN (Paper Trading)"
echo "  Wallet:   \$1000 USDT (simulated)"
echo "  Strategy: UniversalMACDSafe"
echo "  Pairs:    BTC, ETH, BNB, SOL, XRP + 5 more"
echo "  Exchange: Binance (public data only)"
echo ""
echo "  API / UI: http://127.0.0.1:8080"
echo "  User:     freqtrader"
echo "  Pass:     freqtrader"
echo ""
echo "  Press Ctrl+C to stop."
echo "============================================"
echo ""

"$SCRIPT_DIR/.venv/bin/freqtrade" trade \
    --config config.json \
    --strategy UniversalMACDSafe \
    --db-url sqlite:///user_data/tradesv3.dryrun.sqlite
