# freqtrade_mcp.py — Updated for mcp 1.x + freqtrade-client 2026.x compatibility
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List

from freqtrade_client.ft_rest_client import FtRestClient
from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger("freqtrade-mcp")

# Configuration loaded from environment variables
FREQTRADE_API_URL = os.getenv("FREQTRADE_API_URL", "http://127.0.0.1:8080")
USERNAME = os.getenv("FREQTRADE_USERNAME", "freqtrader")
PASSWORD = os.getenv("FREQTRADE_PASSWORD", "freqtrader")


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage the lifecycle of the Freqtrade REST client without failing if bot starts later."""
    client = FtRestClient(FREQTRADE_API_URL, USERNAME, PASSWORD)
    try:
        ping_res = client.ping()
        if ping_res and ping_res.get("status") == "pong":
            logger.info("Connected to Freqtrade API at %s", FREQTRADE_API_URL)
        else:
            logger.warning(
                "Freqtrade API at %s is not running yet (%s). Tools will retry when invoked.",
                FREQTRADE_API_URL,
                ping_res,
            )
    except Exception as exc:
        logger.warning("Initial Freqtrade ping failed (%s); continuing lazily.", exc)

    try:
        yield {"client": client}
    finally:
        logger.info("Freqtrade API client closed")


mcp = FastMCP("FreqtradeMCP", dependencies=["freqtrade-client"], lifespan=app_lifespan)


def _get_client(ctx: Context) -> FtRestClient:
    return ctx.request_context.lifespan_context["client"]


def _format_result(res: Any) -> str:
    if res is None:
        return json.dumps(
            {
                "error": f"Could not reach Freqtrade REST API at {FREQTRADE_API_URL}. "
                "Ensure Freqtrade is running (e.g. ./run_paper_trade.sh)."
            }
        )
    if isinstance(res, str):
        return res
    return json.dumps(res, default=str)


@mcp.tool()
def ping_bot(ctx: Context) -> str:
    """Check if the Freqtrade bot REST API is reachable and running."""
    client = _get_client(ctx)
    return _format_result(client.ping())


@mcp.tool()
def fetch_market_data(pair: str, timeframe: str, ctx: Context, limit: int = 100) -> str:
    """
    Fetch analyzed OHLCV/indicator candles for a specified trading pair and timeframe.

    Parameters:
        pair (str): Trading pair (e.g., "BTC/USDT").
        timeframe (str): Timeframe for the data (e.g., "5m", "1h").
        limit (int): Maximum number of recent candles to return.
    """
    client = _get_client(ctx)
    return _format_result(client.pair_candles(pair=pair, timeframe=timeframe, limit=limit))


@mcp.tool()
def fetch_bot_status(ctx: Context) -> str:
    """Retrieve the current status of open trades."""
    client = _get_client(ctx)
    return _format_result(client.status())


@mcp.tool()
def fetch_profit(ctx: Context) -> str:
    """Get overall profit summary for the trading bot."""
    client = _get_client(ctx)
    return _format_result(client.profit())


@mcp.tool()
def fetch_daily_profit(ctx: Context, days: int = 7) -> str:
    """Get daily profit breakdown for the last N days."""
    client = _get_client(ctx)
    return _format_result(client.daily(days=days))


@mcp.tool()
def fetch_balance(ctx: Context) -> str:
    """Fetch the current wallet/account balance."""
    client = _get_client(ctx)
    return _format_result(client.balance())


@mcp.tool()
def fetch_performance(ctx: Context) -> str:
    """Retrieve per-pair trading performance metrics."""
    client = _get_client(ctx)
    return _format_result(client.performance())


@mcp.tool()
def fetch_stats(ctx: Context) -> str:
    """Retrieve trade duration and exit-reason statistics."""
    client = _get_client(ctx)
    return _format_result(client.stats())


@mcp.tool()
def fetch_whitelist(ctx: Context) -> str:
    """Get the current whitelist of trading pairs."""
    client = _get_client(ctx)
    return _format_result(client.whitelist())


@mcp.tool()
def fetch_blacklist(ctx: Context) -> str:
    """Get the current blacklist of trading pairs."""
    client = _get_client(ctx)
    return _format_result(client.blacklist())


@mcp.tool()
def fetch_trades(ctx: Context, limit: int = 50) -> str:
    """Fetch closed/open trade history."""
    client = _get_client(ctx)
    return _format_result(client.trades(limit=limit))


@mcp.tool()
def fetch_config(ctx: Context) -> str:
    """Retrieve the current sanitized bot configuration (dry_run, strategy, stake, etc.)."""
    client = _get_client(ctx)
    return _format_result(client.show_config())


@mcp.tool()
def fetch_locks(ctx: Context) -> str:
    """Get the current active pair trade locks."""
    client = _get_client(ctx)
    return _format_result(client.locks())


@mcp.tool()
def fetch_logs(ctx: Context, limit: int = 50) -> str:
    """Fetch the latest Freqtrade log lines."""
    client = _get_client(ctx)
    return _format_result(client.logs(limit=limit))


@mcp.tool()
def place_trade(pair: str, side: str, stake_amount: float, ctx: Context) -> str:
    """
    Force-enter a trade via Freqtrade (requires force_entry_enable=true in config).

    Parameters:
        pair (str): Trading pair (e.g., "BTC/USDT").
        side (str): "long" (or "buy") or "short".
        stake_amount (float): Stake amount in stake currency.
    """
    client = _get_client(ctx)
    normalized = side.lower()
    if normalized in ("buy", "long"):
        ft_side = "long"
    elif normalized == "short":
        ft_side = "short"
    else:
        return json.dumps({"error": "side must be 'long', 'buy', or 'short'. Use force_exit to close an existing trade."})
    return _format_result(client.forceenter(pair=pair, side=ft_side, stake_amount=stake_amount))


@mcp.tool()
def force_exit(trade_id: str, ctx: Context, order_type: str | None = None, amount: float | None = None) -> str:
    """Force-exit an open trade by trade_id (or 'all')."""
    client = _get_client(ctx)
    return _format_result(client.forceexit(tradeid=trade_id, ordertype=order_type, amount=amount))


@mcp.tool()
def start_bot(ctx: Context) -> str:
    """Start the Freqtrade trading loop."""
    client = _get_client(ctx)
    return _format_result(client.start())


@mcp.tool()
def stop_bot(ctx: Context) -> str:
    """Stop the Freqtrade trading loop."""
    client = _get_client(ctx)
    return _format_result(client.stop())


@mcp.tool()
def stop_buy(ctx: Context) -> str:
    """Stop entering new trades while continuing to manage/exit open trades."""
    client = _get_client(ctx)
    return _format_result(client.stopbuy())


@mcp.tool()
def reload_config(ctx: Context) -> str:
    """Reload the Freqtrade bot configuration and strategy."""
    client = _get_client(ctx)
    return _format_result(client.reload_config())


@mcp.tool()
def add_blacklist(pair: str, ctx: Context) -> str:
    """Add a pair to the active blacklist."""
    client = _get_client(ctx)
    return _format_result(client.blacklist(pair))


@mcp.tool()
def delete_blacklist(pair: str, ctx: Context) -> str:
    """Remove a pair from the active blacklist."""
    client = _get_client(ctx)
    return _format_result(client._delete("blacklist", params={"pairs_to_delete": pair}))


@mcp.tool()
def delete_lock(lock_id: int, ctx: Context) -> str:
    """Delete a specific trade lock by ID."""
    client = _get_client(ctx)
    return _format_result(client.delete_lock(lock_id))


@mcp.prompt()
def analyze_trade(pair: str, timeframe: str, ctx: Context) -> List[Dict[str, Any]]:
    """Generate a prompt to analyze a trading pair's performance."""
    market_data = fetch_market_data(pair, timeframe, ctx)
    return [
        {"role": "user", "content": f"Analyze the recent performance of {pair} over {timeframe}. Market data: {market_data}"},
        {"role": "assistant", "content": f"I'll analyze the market data for {pair} and provide insights."},
    ]


@mcp.prompt()
def trading_strategy(ctx: Context) -> str:
    """Generate a prompt for reviewing current bot status and suggesting improvements."""
    return "Based on the current bot status, profit, and market conditions, review performance and risk controls."


if __name__ == "__main__":
    mcp.run()
