"""Main trading bot loop."""

from __future__ import annotations

from loguru import logger

import src.config as cfg
from src.broker import AlpacaBroker
from src.strategy import Signal, crossover_occurred


class TradingBot:
    def __init__(self) -> None:
        self.broker = AlpacaBroker()
        self.all_symbols = cfg.STOCK_SYMBOLS + cfg.CRYPTO_SYMBOLS
        logger.info(f"Watching symbols: {self.all_symbols}")
        logger.info(f"MA windows: short={cfg.SHORT_WINDOW} long={cfg.LONG_WINDOW}")

    def run_once(self) -> None:
        """Evaluate all symbols and act on crossover signals."""
        equity = self.broker.get_equity()
        cash = self.broker.get_cash()
        logger.info(f"Account — equity=${equity:.2f} cash=${cash:.2f}")

        for symbol in self.all_symbols:
            self._process(symbol)

    def _process(self, symbol: str) -> None:
        try:
            bars = self.broker.get_bars(symbol, cfg.LOOKBACK_BARS)
            if len(bars) < cfg.LONG_WINDOW + 1:
                logger.warning(f"{symbol}: not enough bars ({len(bars)} < {cfg.LONG_WINDOW + 1}), skipping")
                return

            signal = crossover_occurred(bars, cfg.SHORT_WINDOW, cfg.LONG_WINDOW)
            last_close = bars["close"].iloc[-1]
            logger.info(f"{symbol} close={last_close:.4f} signal={signal.value}")

            if signal == Signal.BUY:
                self.broker.buy(symbol)
            elif signal == Signal.SELL:
                self.broker.sell(symbol)

        except Exception as exc:
            logger.error(f"{symbol} processing error: {exc}")
