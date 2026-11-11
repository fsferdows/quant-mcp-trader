"""
MultiIndicatorStrategy - Trend-filtered pullback & momentum strategy for Freqtrade.

Combines multi-timeframe EMA trend alignment, RSI pullback zone, MACD momentum,
ADX trend strength, Bollinger Band value positioning, and volume confirmation,
paired with strategy-level protections and dynamic trailing stop-loss.
"""

from functools import reduce
import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import DecimalParameter, IntParameter, IStrategy, merge_informative_pair
from pandas import DataFrame


class MultiIndicatorStrategy(IStrategy):
    """Multi-timeframe trend-aligned strategy with strict risk protections."""

    INTERFACE_VERSION = 3
    timeframe = "5m"
    can_short = False

    minimal_roi = {
        "0": 0.04,
        "30": 0.025,
        "90": 0.015,
        "180": 0.005,
    }

    stoploss = -0.04
    use_custom_stoploss = True

    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
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

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC",
    }

    buy_rsi_low = IntParameter(20, 40, default=30, space="buy", optimize=True)
    buy_ema_fast = IntParameter(5, 20, default=9, space="buy", optimize=True)
    buy_ema_slow = IntParameter(20, 60, default=21, space="buy", optimize=True)
    buy_adx_min = IntParameter(15, 35, default=20, space="buy", optimize=True)
    buy_volume_factor = DecimalParameter(1.0, 3.0, default=1.2, decimals=1, space="buy", optimize=True)
    buy_bb_factor = DecimalParameter(0.97, 1.0, default=0.99, decimals=2, space="buy", optimize=True)
    sell_rsi_high = IntParameter(60, 85, default=72, space="sell", optimize=True)

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        return [(pair, "1h") for pair in pairs]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for period in [5, 8, 9, 13, 21, 34, 50, 100, 200]:
            dataframe[f"ema_{period}"] = ta.EMA(dataframe, timeperiod=period)

        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        stoch_rsi = ta.STOCHRSI(dataframe, timeperiod=14, fastk_period=3, fastd_period=3)
        dataframe["stochrsi_k"] = stoch_rsi["fastk"]
        dataframe["stochrsi_d"] = stoch_rsi["fastd"]

        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe["macdhist"] = macd["macdhist"]

        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe["bb_lowerband"] = bollinger["lowerband"]
        dataframe["bb_middleband"] = bollinger["middleband"]
        dataframe["bb_upperband"] = bollinger["upperband"]

        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["plus_di"] = ta.PLUS_DI(dataframe, timeperiod=14)
        dataframe["minus_di"] = ta.MINUS_DI(dataframe, timeperiod=14)

        dataframe["volume_mean_20"] = dataframe["volume"].rolling(window=20).mean()
        dataframe["volume_ratio"] = dataframe["volume"] / (dataframe["volume_mean_20"] + 1e-10)
        dataframe["mfi"] = ta.MFI(dataframe, timeperiod=14)

        if self.dp:
            informative = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe="1h")
            if not informative.empty:
                informative["ema_50"] = ta.EMA(informative, timeperiod=50)
                informative["ema_200"] = ta.EMA(informative, timeperiod=200)
                informative["rsi"] = ta.RSI(informative, timeperiod=14)
                dataframe = merge_informative_pair(
                    dataframe,
                    informative[["date", "ema_50", "ema_200", "rsi"]],
                    self.timeframe,
                    "1h",
                    ffill=True,
                )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = [
            dataframe[f"ema_{self.buy_ema_fast.value}"] > dataframe[f"ema_{self.buy_ema_slow.value}"],
            (dataframe["rsi"] > self.buy_rsi_low.value) & (dataframe["rsi"] < 62),
            dataframe["macdhist"] > 0,
            dataframe["close"] < dataframe["bb_middleband"] * (1 / self.buy_bb_factor.value),
            dataframe["adx"] > self.buy_adx_min.value,
            dataframe["plus_di"] > dataframe["minus_di"],
            dataframe["volume_ratio"] > self.buy_volume_factor.value,
            dataframe["mfi"] < 78,
            (dataframe["stochrsi_k"] > dataframe["stochrsi_d"]) & (dataframe["stochrsi_k"] < 80),
            dataframe["volume"] > 0,
        ]
        if "ema_50_1h" in dataframe.columns:
            conditions.append(dataframe["ema_50_1h"] > dataframe["ema_200_1h"])

        dataframe.loc[reduce(lambda x, y: x & y, conditions), ["enter_long", "enter_tag"]] = (
            1,
            "multi_confluence",
        )
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["rsi"] > self.sell_rsi_high.value)
            & ((dataframe["macdhist"] < 0) | (dataframe["close"] > dataframe["bb_upperband"]))
            & (dataframe["volume"] > 0),
            ["exit_long", "exit_tag"],
        ] = (1, "overbought_exit")
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> float:
        if current_profit > 0.02:
            return -0.005
        if current_profit > 0.01:
            return -0.01
        return self.stoploss

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
