#!/bin/bash
# ============================================================
# Customize Bot Name, API Username & Password
# ============================================================
# Updates config.json and syncs .agents/plugins/freqtrade-trading/mcp_config.json
# so you can log into FreqUI (http://localhost:8080) with your own credentials.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"
MCP_FILE="$SCRIPT_DIR/.agents/plugins/freqtrade-trading/mcp_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ config.json not found. Run ./setup.sh first."
    exit 1
fi

read -p "Bot Name [CryptoPaperTrader]: " INPUT_BOT_NAME
read -p "Username [freqtrader]: " INPUT_USERNAME
read -s -p "Password [freqtrader]: " INPUT_PASSWORD
echo ""

BOT_NAME="${INPUT_BOT_NAME:-CryptoPaperTrader}"
USERNAME="${INPUT_USERNAME:-freqtrader}"
PASSWORD="${INPUT_PASSWORD:-freqtrader}"

python3 - "$CONFIG_FILE" "$MCP_FILE" "$BOT_NAME" "$USERNAME" "$PASSWORD" << 'PYEOF'
import json, os, sys

cfg_path, mcp_path, bot_name, username, password = sys.argv[1:6]

with open(cfg_path) as f:
    cfg = json.load(f)

cfg["bot_name"] = bot_name
cfg.setdefault("api_server", {})
cfg["api_server"]["username"] = username
cfg["api_server"]["password"] = password

with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=4)

if os.path.exists(mcp_path):
    with open(mcp_path) as f:
        mcp = json.load(f)
    ft = mcp.get("mcpServers", {}).get("freqtrade-mcp")
    if ft is not None:
        ft.setdefault("env", {})
        ft["env"]["FREQTRADE_USERNAME"] = username
        ft["env"]["FREQTRADE_PASSWORD"] = password
        with open(mcp_path, "w") as f:
            json.dump(mcp, f, indent=2)
PYEOF

echo "✅ Updated credentials in config.json (and synced mcp_config.json)."
echo "   Restart ./run_paper_trade.sh for changes to take effect."
