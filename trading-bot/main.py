#!/usr/bin/env python3
"""
Alpaca Trading Bot — Moving Average Crossover
Run:  python main.py            (runs once immediately, then on schedule)
      python main.py --once     (runs once and exits)
"""

import argparse
import sys
import time

import schedule
from loguru import logger

from src.bot import TradingBot
import src.config as cfg

# Map timeframe string to schedule interval in minutes
SCHEDULE_MAP = {
    "1Min": 1,
    "5Min": 5,
    "15Min": 15,
    "1Hour": 60,
    "1Day": 60 * 24,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Alpaca MA Crossover Trading Bot")
    parser.add_argument("--once", action="store_true", help="Run one evaluation cycle and exit")
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}", level="DEBUG")
    logger.add("bot.log", rotation="10 MB", retention="7 days", level="INFO")

    logger.info("=" * 60)
    logger.info(f"Alpaca Trading Bot starting — mode={cfg.TRADING_MODE.upper()}")
    logger.info("=" * 60)

    bot = TradingBot()

    if args.once:
        bot.run_once()
        return

    interval_minutes = SCHEDULE_MAP.get(cfg.TIMEFRAME, 60)
    logger.info(f"Scheduling evaluation every {interval_minutes} minute(s)")

    # Run immediately on startup, then on schedule
    bot.run_once()
    schedule.every(interval_minutes).minutes.do(bot.run_once)

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")


if __name__ == "__main__":
    main()
