"""Moving Average Crossover strategy."""

import pandas as pd
from enum import Enum


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


def compute_signals(bars: pd.DataFrame, short_window: int, long_window: int) -> pd.DataFrame:
    """
    Compute moving average crossover signals on a bars DataFrame.

    bars must have a 'close' column indexed by datetime.
    Returns the same DataFrame with added columns: short_ma, long_ma, signal.
    """
    df = bars.copy()
    df["short_ma"] = df["close"].rolling(window=short_window).mean()
    df["long_ma"] = df["close"].rolling(window=long_window).mean()

    df["signal"] = Signal.HOLD.value
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = Signal.BUY.value
    df.loc[df["short_ma"] < df["long_ma"], "signal"] = Signal.SELL.value

    return df


def latest_signal(bars: pd.DataFrame, short_window: int, long_window: int) -> Signal:
    """Return the signal for the most recent completed bar."""
    if len(bars) < long_window:
        return Signal.HOLD

    df = compute_signals(bars, short_window, long_window)
    last = df.iloc[-1]["signal"]
    return Signal(last)


def crossover_occurred(bars: pd.DataFrame, short_window: int, long_window: int) -> Signal:
    """
    Return BUY if a bullish crossover just happened on the last two bars,
    SELL if a bearish crossover just happened, HOLD otherwise.
    Avoids re-entering the same side on every bar.
    """
    if len(bars) < long_window + 1:
        return Signal.HOLD

    df = compute_signals(bars, short_window, long_window)
    prev = df.iloc[-2]["signal"]
    curr = df.iloc[-1]["signal"]

    if prev != Signal.BUY.value and curr == Signal.BUY.value:
        return Signal.BUY
    if prev != Signal.SELL.value and curr == Signal.SELL.value:
        return Signal.SELL
    return Signal.HOLD
