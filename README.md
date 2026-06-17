# Stock Agent

A monitoring agent that collects prices, key metrics, and news for watchlist tickers
(**NVDA**, **PLTR**) and automatically sends an **HTML report via email**. Designed to
run on a cron schedule at pre-market open and market close.

## Features

- **Prices & metrics** — current price, % change, market cap, short interest,
  institutional ownership, volume (ratio vs. average)
- **News** — latest articles per ticker from Google News RSS
- **Report** — responsive HTML card-style email (mobile-friendly)
- **Auto-send** — delivered to a configured recipient via Gmail SMTP (SSL)
- **Scheduling** — runs at pre-market open / market close (Berlin local time)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your own values.

```bash
cp .env.example .env
```

```dotenv
SENDER_EMAIL=your_sender@gmail.com
RECEIVER_EMAIL=your_receiver@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password   # Gmail App Password (after enabling 2FA)
```

> `GMAIL_APP_PASSWORD` is not your regular account password but a
> [Google App Password](https://myaccount.google.com/apppasswords).

## Usage

```bash
python3 stock_agent.py   # run manually
./run.sh                 # cron wrapper script
```

### Example cron entries

```cron
# Pre-market open (Berlin 14:00) / market close (Berlin 22:00)
0 14 * * 1-5 /path/to/stock_agent/run.sh >> /path/to/stock_agent/cron.log 2>&1
0 22 * * 1-5 /path/to/stock_agent/run.sh >> /path/to/stock_agent/cron.log 2>&1
```

## Tech Stack

- **yfinance** — price & metric data
- **feedparser** — Google News RSS parsing
- **smtplib / email** — Gmail SMTP delivery
- **pytz** — timezone handling

> ⚠️ This is a monitoring tool, not investment advice. Make your own investment
> decisions.
