#!/bin/bash
# ============================================================
# Quant MCP Trader — One-Command Setup Script
# ============================================================
# Clones upstream Freqtrade (if needed), installs Python >=3.12
# dependencies, FreqUI, and all 4 MCP servers for DRY-RUN paper trading.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FT_DIR="$SCRIPT_DIR/freqtrade"
STRAT_DIR="$SCRIPT_DIR/external_strategies/freqtrade-strategies"
MCP_DIR="$SCRIPT_DIR/mcp_servers"

echo "============================================"
echo "  Quant MCP Trader Setup"
echo "============================================"
echo ""
echo "⚠️  Configured for DRY RUN (paper trading) only."
echo "    No real money or exchange API keys are used."
echo ""

if ! command -v uv &>/dev/null; then
    echo "❌ 'uv' is required. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo "❌ 'git' is required."
    exit 1
fi

# Clone upstream repositories if not already present
if [ ! -d "$FT_DIR/.git" ]; then
    echo "→ Cloning freqtrade (shallow)..."
    git clone --depth 1 https://github.com/freqtrade/freqtrade.git "$FT_DIR"
fi

if [ ! -d "$STRAT_DIR/.git" ]; then
    echo "→ Cloning freqtrade-strategies (shallow)..."
    mkdir -p "$SCRIPT_DIR/external_strategies"
    git clone --depth 1 https://github.com/freqtrade/freqtrade-strategies.git "$STRAT_DIR"
fi

# Install system dependencies on macOS
if [ "$(uname -s)" = "Darwin" ] && command -v brew &>/dev/null; then
    echo "→ Ensuring macOS libraries (ta-lib, gettext, libomp)..."
    brew install ta-lib gettext libomp 2>/dev/null || true
    export LDFLAGS="-L/opt/homebrew/opt/ta-lib/lib -L/opt/homebrew/opt/libomp/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/ta-lib/include -I/opt/homebrew/opt/libomp/include"
fi

# Locate or install Python 3.12+
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.12 || command -v python3.13 || true)}"
if [ -z "$PYTHON_BIN" ]; then
    echo "→ Installing Python 3.12 via uv..."
    uv python install 3.12
    PYTHON_BIN="3.12"
fi

echo "→ Creating Freqtrade venv (.venv) with $PYTHON_BIN..."
uv venv "$SCRIPT_DIR/.venv" --python "$PYTHON_BIN"
uv pip install --python "$SCRIPT_DIR/.venv/bin/python" \
    -r "$FT_DIR/requirements.txt" \
    -r "$FT_DIR/requirements-plot.txt" \
    -r "$FT_DIR/requirements-hyperopt.txt" \
    -e "$FT_DIR"

echo "→ Installing FreqUI..."
"$SCRIPT_DIR/.venv/bin/freqtrade" install-ui

echo "→ Creating MCP servers venv (mcp_servers/.venv)..."
uv venv "$MCP_DIR/.venv" --python "$PYTHON_BIN"
uv pip install --python "$MCP_DIR/.venv/bin/python" \
    "mcp[cli]>=1.5.0,<2" \
    "freqtrade-client>=2025.2" \
    "httpx>=0.28.1"

if command -v npm &>/dev/null; then
    echo "→ Installing Node.js MCP server dependencies..."
    (cd "$MCP_DIR/crypto-indicators-mcp" && npm install)
    (cd "$MCP_DIR/ccxt-mcp" && npm install)
else
    echo "⚠️  Node.js/npm not found; skipping Node MCP servers (crypto-indicators-mcp, ccxt-mcp)."
fi

# Generate local config.json from template if missing
if [ ! -f "$SCRIPT_DIR/config.json" ] && [ -f "$SCRIPT_DIR/config.example.json" ]; then
    echo "→ Generating local config.json with a fresh JWT secret..."
    "$SCRIPT_DIR/.venv/bin/python" - << PYEOF
import json, secrets
with open("$SCRIPT_DIR/config.example.json") as f:
    cfg = json.load(f)
cfg["api_server"]["jwt_secret_key"] = secrets.token_hex(32)
with open("$SCRIPT_DIR/config.json", "w") as f:
    json.dump(cfg, f, indent=4)
PYEOF
fi

# Generate local ccxt_config.json for ccxt-mcp if missing
if [ ! -f "$MCP_DIR/ccxt-mcp/ccxt_config.json" ]; then
    cat > "$MCP_DIR/ccxt-mcp/ccxt_config.json" << 'EOF'
{
  "settings": {
    "exchangeOptions": {
      "binance": {
        "fetchMarkets": {
          "types": ["spot"]
        }
      }
    }
  }
}
EOF
    chmod 600 "$MCP_DIR/ccxt-mcp/ccxt_config.json"
fi

# Generate local workspace plugin mcp_config.json from template if missing
MCP_CFG="$SCRIPT_DIR/.agents/plugins/freqtrade-trading/mcp_config.json"
MCP_TPL="$SCRIPT_DIR/.agents/plugins/freqtrade-trading/mcp_config.example.json"
if [ ! -f "$MCP_CFG" ] && [ -f "$MCP_TPL" ]; then
    NODE_BIN="$(command -v node || echo node)"
    sed -e "s|__REPO_ROOT__|$SCRIPT_DIR|g" -e "s|__NODE_BIN__|$NODE_BIN|g" "$MCP_TPL" > "$MCP_CFG"
    echo "→ Generated workspace MCP config at $MCP_CFG"
fi

mkdir -p "$SCRIPT_DIR/user_data/data" "$SCRIPT_DIR/user_data/logs" "$SCRIPT_DIR/user_data/backtest_results"

echo ""
echo "→ Verifying Freqtrade installation..."
"$SCRIPT_DIR/.venv/bin/freqtrade" --version

echo ""
echo "============================================"
echo "  ✅ Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Download data:  ./run_backtest.sh download"
echo "  2. Run backtest:   ./run_backtest.sh"
echo "  3. Audit bias:     ./run_backtest.sh audit"
echo "  4. Paper trade:    ./run_paper_trade.sh"
echo ""
