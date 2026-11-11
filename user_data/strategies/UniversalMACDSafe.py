"""
UniversalMACDSafe - Risk-hardened adaptation of UniversalMACD (freqtrade-strategies).

Enhancements over upstream UniversalMACD:
- startup_candle_count increased from 30 to 200 (eliminates EMA recursive warm-up drift)
- Tightened hard stoploss from -31.8% to -8.0% for capital preservation
- Added strategy-level protections (CooldownPeriod, StoplossGuard, MaxDrawdown)
- Spot-only 1x leverage guard
"""

import talib.abstract as ta
from freqtrade.strategy import DecimalParameter, IStrategy
from pandas import DataFrame


class UniversalMACDSafe(IStrategy):
    """Normalized EMA-spread mean-reversion strategy with strict risk protections."""

    INTERFACE_VERSION = 3
    timeframe = "5m"
    can_short = False

    minimal_roi = {
        "0": 0.213,
        "27": 0.099,
        "60": 0.03,
        "164": 0,
    }

    # Tightened from -0.318 to -0.08 for strict drawdown control
    stoploss = -0.08

    trailing_stop = False
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = True

    # 200 candles eliminates recursive EMA warm-up variance (verified via recursive-analysis)
    startup_candle_count: int = 200

    protections = [
        {
            "method": "CooldownPeriod",
            "stop_duration_candles": 6,
        },
        {
            "method": "StoplossGuard",
            "lookback_period_candles": 288,
            "trade_limit": 2,
            "stop_duration_candles": 24,
            "only_per_pair": False,
        },
        {
            "method": "MaxDrawdown",
            "lookback_period_candles": 288,
            "max_allowed_drawdown": 0.10,
            "stop_duration_candles": 48,
            "trade_limit": 4,
        },
    ]

    buy_umacd_max = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.01176, space="buy")
    buy_umacd_min = DecimalParameter(-0.05, 0.05, decimals=5, default=-0.01416, space="buy")
    sell_umacd_min = DecimalParameter(0.001, 0.05, decimals=5, default=0.00800, space="sell")
    sell_umacd_max = DecimalParameter(0.005, 0.08, decimals=5, default=0.02500, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ma12"] = ta.EMA(dataframe, timeperiod=12)
        dataframe["ma26"] = ta.EMA(dataframe, timeperiod=26)
        dataframe["umacd"] = (dataframe["ma12"] / dataframe["ma26"]) - 1.0
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                dataframe["umacd"].between(self.buy_umacd_min.value, self.buy_umacd_max.value)
                & (dataframe["volume"] > 0)
            ),
            ["enter_long", "enter_tag"],
        ] = (1, "umacd_dip")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                dataframe["umacd"].between(self.sell_umacd_min.value, self.sell_umacd_max.value)
                & (dataframe["volume"] > 0)
            ),
            ["exit_long", "exit_tag"],
        ] = (1, "umacd_exit")
        return dataframe

    def leverage(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag,
        side: str,
        **kwargs,
    ) -> float:
        return 1.0
