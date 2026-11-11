#!/bin/bash
# ============================================================
# Freqtrade Backtesting Script
# ============================================================
# Downloads historical data and runs backtests.
# Usage:
#   ./run_backtest.sh download   - Download historical data
#   ./run_backtest.sh             - Run backtest
#   ./run_backtest.sh hyperopt   - Run hyperparameter optimization
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv
source "$SCRIPT_DIR/.venv/bin/activate" 2>/dev/null || {
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
}

ACTION="${1:-backtest}"

case "$ACTION" in
    download)
        echo "============================================"
        echo "  Downloading Historical Data"
        echo "============================================"
        echo ""

        # Download 5m data for the last 90 days
        freqtrade download-data \
            --config config.json \
            --timeframe 5m 15m 1h 4h 1d \
            --days 90

        echo ""
        echo "✅ Data download complete!"
        ;;

    backtest)
        echo "============================================"
        echo "  Running Backtest"
        echo "============================================"
        echo ""

        freqtrade backtesting \
            --config config.json \
            --strategy UniversalMACDSafe \
            --timeframe 5m \
            --timerange 20260824- \
            --enable-protections \
            --cache none

        echo ""
        echo "✅ Backtest complete! Check user_data/backtest_results/"
        ;;

    audit)
        echo "============================================"
        echo "  Running Lookahead & Recursive Bias Audit"
        echo "============================================"
        echo ""

        freqtrade lookahead-analysis \
            --config config.json \
            --strategy UniversalMACDSafe \
            --timeframe 5m \
            --timerange 20260824-

        freqtrade recursive-analysis \
            --config config.json \
            --strategy UniversalMACDSafe \
            --timeframe 5m \
            --timerange 20260824-
        ;;

    hyperopt)
        echo "============================================"
        echo "  Running Hyperparameter Optimization"
        echo "============================================"
        echo ""

        freqtrade hyperopt \
            --config config.json \
            --strategy UniversalMACDSafe \
            --hyperopt-loss SharpeHyperOptLossDaily \
            --timeframe 5m \
            --epochs 200 \
            --spaces buy sell \
            --min-trades 20

        echo ""
        echo "✅ Hyperopt complete!"
        ;;

    *)
        echo "Usage: $0 {download|backtest|audit|hyperopt}"
        exit 1
        ;;
esac
