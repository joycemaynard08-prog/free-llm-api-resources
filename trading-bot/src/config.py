import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Required env var {key!r} is not set. Copy .env.example to .env and fill it in.")
    return val


def _symbols(key: str, default: str) -> list[str]:
    raw = os.getenv(key, default)
    return [s.strip() for s in raw.split(",") if s.strip()]


API_KEY = _require("ALPACA_API_KEY")
SECRET_KEY = _require("ALPACA_SECRET_KEY")

TRADING_MODE = os.getenv("TRADING_MODE", "paper").lower()
if TRADING_MODE not in ("paper", "live"):
    raise ValueError("TRADING_MODE must be 'paper' or 'live'")

PAPER = TRADING_MODE == "paper"

STOCK_BASE_URL = "https://paper-api.alpaca.markets" if PAPER else "https://api.alpaca.markets"
CRYPTO_BASE_URL = STOCK_BASE_URL  # same endpoint for both asset classes

STOCK_SYMBOLS = _symbols("STOCK_SYMBOLS", "AAPL,MSFT,SPY")
CRYPTO_SYMBOLS = _symbols("CRYPTO_SYMBOLS", "BTC/USD,ETH/USD")

SHORT_WINDOW = int(os.getenv("SHORT_WINDOW", "20"))
LONG_WINDOW = int(os.getenv("LONG_WINDOW", "50"))

MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.1"))

TIMEFRAME = os.getenv("TIMEFRAME", "1Hour")

LOOKBACK_BARS = int(os.getenv("LOOKBACK_BARS", "200"))
