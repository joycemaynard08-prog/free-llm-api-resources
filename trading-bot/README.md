# Alpaca Trading Bot

A Moving Average Crossover trading bot for Alpaca Markets — supports both **stocks/ETFs** and **crypto**, with **paper** and **live** trading modes.

## Strategy

**MA Crossover**: buys when the short-period moving average crosses above the long-period MA (bullish crossover), and sells when it crosses below (bearish crossover). Only acts on the crossover event — not on every bar where one MA is above the other — to avoid churning.

## Setup

### 1. Install dependencies

```bash
cd trading-bot
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` with your Alpaca API key and secret. Get them at:  
https://app.alpaca.markets → Account → API Keys

### 3. Run (paper mode by default)

```bash
# Run continuously (evaluates on each completed bar)
python main.py

# Run one cycle and exit
python main.py --once
```

## Configuration

All settings live in `.env`:

| Variable | Default | Description |
|---|---|---|
| `ALPACA_API_KEY` | — | Required |
| `ALPACA_SECRET_KEY` | — | Required |
| `TRADING_MODE` | `paper` | `paper` or `live` |
| `STOCK_SYMBOLS` | `AAPL,MSFT,SPY` | Comma-separated tickers |
| `CRYPTO_SYMBOLS` | `BTC/USD,ETH/USD` | Comma-separated pairs |
| `SHORT_WINDOW` | `20` | Short MA period (bars) |
| `LONG_WINDOW` | `50` | Long MA period (bars) |
| `MAX_POSITION_SIZE` | `0.1` | Max position as fraction of equity |
| `TIMEFRAME` | `1Hour` | Bar size: `1Min` `5Min` `15Min` `1Hour` `1Day` |
| `LOOKBACK_BARS` | `200` | Historical bars to load |

## Project structure

```
trading-bot/
├── main.py          # Entry point + scheduler
├── src/
│   ├── config.py    # Env var loading
│   ├── strategy.py  # MA crossover signal computation
│   ├── broker.py    # Alpaca API wrapper (orders + data)
│   └── bot.py       # Main loop
├── requirements.txt
└── .env.example
```

## Risk warnings

- **Always start in paper mode** and validate behaviour before switching to live.
- `MAX_POSITION_SIZE=0.1` limits each position to 10% of equity by default.
- This bot places **market orders** — slippage can occur, especially for illiquid assets.
- Past strategy performance does not guarantee future results.
- You are responsible for all trades placed by this bot.
