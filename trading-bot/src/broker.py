"""Alpaca broker interface — handles stocks and crypto uniformly."""

from __future__ import annotations

import pandas as pd
from loguru import logger

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetAssetsRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

import src.config as cfg


def _parse_timeframe(tf: str) -> TimeFrame:
    mapping = {
        "1Min": TimeFrame(1, TimeFrameUnit.Minute),
        "5Min": TimeFrame(5, TimeFrameUnit.Minute),
        "15Min": TimeFrame(15, TimeFrameUnit.Minute),
        "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
        "1Day": TimeFrame(1, TimeFrameUnit.Day),
    }
    if tf not in mapping:
        raise ValueError(f"Unknown TIMEFRAME {tf!r}. Choose from: {list(mapping)}")
    return mapping[tf]


class AlpacaBroker:
    def __init__(self) -> None:
        self.trading = TradingClient(cfg.API_KEY, cfg.SECRET_KEY, paper=cfg.PAPER)
        self.stock_data = StockHistoricalDataClient(cfg.API_KEY, cfg.SECRET_KEY)
        self.crypto_data = CryptoHistoricalDataClient(cfg.API_KEY, cfg.SECRET_KEY)
        self.timeframe = _parse_timeframe(cfg.TIMEFRAME)
        logger.info(f"Broker initialised — mode={cfg.TRADING_MODE.upper()} timeframe={cfg.TIMEFRAME}")

    # ------------------------------------------------------------------
    # Account helpers
    # ------------------------------------------------------------------

    def get_equity(self) -> float:
        account = self.trading.get_account()
        return float(account.equity)

    def get_cash(self) -> float:
        account = self.trading.get_account()
        return float(account.cash)

    def get_position_qty(self, symbol: str) -> float:
        """Return current position quantity (0 if no position)."""
        try:
            pos = self.trading.get_open_position(symbol.replace("/", ""))
            return float(pos.qty)
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # Historical data
    # ------------------------------------------------------------------

    def get_bars(self, symbol: str, lookback: int) -> pd.DataFrame:
        """Fetch the last `lookback` bars for a symbol. Returns DataFrame with 'close'."""
        from datetime import datetime, timedelta, timezone

        end = datetime.now(timezone.utc)
        # Generous window to account for weekends / holidays
        start = end - timedelta(days=lookback * 3)

        is_crypto = "/" in symbol
        if is_crypto:
            req = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=self.timeframe,
                start=start,
                end=end,
                limit=lookback,
            )
            bars = self.crypto_data.get_crypto_bars(req).df
        else:
            req = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=self.timeframe,
                start=start,
                end=end,
                limit=lookback,
            )
            bars = self.stock_data.get_stock_bars(req).df

        # Flatten multi-index if present
        if isinstance(bars.index, pd.MultiIndex):
            bars = bars.xs(symbol, level="symbol")

        bars = bars.sort_index()
        return bars[["close"]].tail(lookback)

    # ------------------------------------------------------------------
    # Order execution
    # ------------------------------------------------------------------

    def _notional_for_symbol(self, symbol: str) -> float:
        """Dollar amount to deploy (MAX_POSITION_SIZE × equity)."""
        return self.get_equity() * cfg.MAX_POSITION_SIZE

    def buy(self, symbol: str) -> None:
        notional = self._notional_for_symbol(symbol)
        cash = self.get_cash()
        if notional > cash:
            logger.warning(f"Not enough cash to buy {symbol}: need ${notional:.2f}, have ${cash:.2f}")
            return

        alpaca_symbol = symbol.replace("/", "")
        req = MarketOrderRequest(
            symbol=alpaca_symbol,
            notional=round(notional, 2),
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
        )
        order = self.trading.submit_order(req)
        logger.info(f"BUY {symbol} ${notional:.2f} — order_id={order.id}")

    def sell(self, symbol: str) -> None:
        qty = self.get_position_qty(symbol)
        if qty <= 0:
            logger.debug(f"No position to sell for {symbol}")
            return

        alpaca_symbol = symbol.replace("/", "")
        req = MarketOrderRequest(
            symbol=alpaca_symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        order = self.trading.submit_order(req)
        logger.info(f"SELL {symbol} qty={qty} — order_id={order.id}")
