#!/usr/bin/env python3
"""
주식 모니터링 에이전트 - NVDA & PLTR
장 시작 전(독일 14:00) / 장 마감(독일 22:00) 자동 실행
"""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import feedparser
import pytz
import yfinance as yf
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

TICKERS = ["NVDA", "PLTR"]


def get_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info

    current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)

    if current_price and prev_close:
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
    else:
        change = 0.0
        change_pct = 0.0

    short_percent = info.get("shortPercentOfFloat") or 0
    institutional_pct = info.get("heldPercentInstitutions") or 0

    return {
        "ticker": ticker,
        "name": info.get("shortName", ticker),
        "price": current_price,
        "change": change,
        "change_pct": change_pct,
        "short_percent": short_percent * 100,
        "institutional_pct": institutional_pct * 100,
        "market_cap": info.get("marketCap"),
        "volume": info.get("volume") or 0,
        "avg_volume": info.get("averageVolume") or 0,
    }


def get_news(ticker: str, num_articles: int = 3) -> list:
    url = (
        f"https://news.google.com/rss/search"
        f"?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    )
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:num_articles]:
        articles.append({
            "title": entry.get("title", "(제목 없음)"),
            "link": entry.get("link", "#"),
            "published": entry.get("published", ""),
        })
    return articles


def format_market_cap(num) -> str:
    if not num:
        return "N/A"
    if num >= 1e12:
        return f"${num / 1e12:.2f}T"
    if num >= 1e9:
        return f"${num / 1e9:.2f}B"
    if num >= 1e6:
        return f"${num / 1e6:.2f}M"
    return f"${num:,.0f}"


def build_html(stocks_data: list, news_data: dict) -> str:
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    date_str = now.strftime("%Y년 %m월 %d일 %H:%M (독일 현지시각)")

    # ── 헤더 ──────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>주식 리포트</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
           background: #f0f2f5; padding: 24px; color: #1a1a2e; }}
    .wrap {{ max-width: 680px; margin: 0 auto; }}
    .hdr {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff; padding: 28px 24px; border-radius: 14px 14px 0 0; text-align: center; }}
    .hdr h1 {{ font-size: 20px; font-weight: 700; letter-spacing: 0.5px; }}
    .hdr p  {{ margin-top: 6px; font-size: 12px; opacity: 0.65; }}
    .card {{ background: #fff; border-radius: 14px; padding: 22px;
             margin: 14px 0; box-shadow: 0 2px 12px rgba(0,0,0,0.07); }}
    .stock-top {{ display: flex; justify-content: space-between; align-items: flex-start; }}
    .t-name {{ font-size: 26px; font-weight: 800; }}
    .t-full  {{ font-size: 12px; color: #888; margin-top: 3px; }}
    .t-price {{ font-size: 30px; font-weight: 800; text-align: right; }}
    .pos {{ color: #00c853; font-size: 15px; font-weight: 600; }}
    .neg {{ color: #f44336; font-size: 15px; font-weight: 600; }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 16px; }}
    .m {{ background: #f7f8fa; border-radius: 10px; padding: 12px; text-align: center; }}
    .m-lbl {{ font-size: 10px; color: #999; text-transform: uppercase; letter-spacing: 0.6px; }}
    .m-val {{ font-size: 15px; font-weight: 700; margin-top: 5px; }}
    .sec-title {{ font-size: 12px; font-weight: 700; color: #555;
                  text-transform: uppercase; letter-spacing: 1px;
                  border-bottom: 2px solid #f0f2f5; padding-bottom: 8px;
                  margin: 20px 0 12px; }}
    .news-item {{ padding: 10px 0; border-bottom: 1px solid #f5f5f5; }}
    .news-item:last-child {{ border-bottom: none; }}
    .news-a {{ font-size: 13px; font-weight: 600; color: #1a1a2e;
               text-decoration: none; line-height: 1.5; }}
    .news-a:hover {{ color: #0055cc; }}
    .news-date {{ font-size: 11px; color: #aaa; margin-top: 3px; }}
    .footer {{ text-align: center; padding: 16px; font-size: 11px; color: #bbb; }}
  </style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <h1>📊 주식 모니터링 리포트</h1>
    <p>{date_str}</p>
  </div>
"""

    # ── 종목별 카드 ───────────────────────────────────────────
    for d in stocks_data:
        chg_cls = "pos" if d["change_pct"] >= 0 else "neg"
        sign    = "+" if d["change_pct"] >= 0 else ""
        arrow   = "▲" if d["change_pct"] >= 0 else "▼"

        short_str = f"{d['short_percent']:.1f}%" if d["short_percent"] else "N/A"
        inst_str  = f"{d['institutional_pct']:.1f}%" if d["institutional_pct"] else "N/A"

        vol_ratio = ""
        if d["volume"] and d["avg_volume"]:
            vol_ratio = f"<br><small>평균 대비 {d['volume']/d['avg_volume']:.1f}x</small>"

        html += f"""
  <div class="card">
    <div class="stock-top">
      <div>
        <div class="t-name">{d['ticker']}</div>
        <div class="t-full">{d['name']}</div>
      </div>
      <div>
        <div class="t-price">${d['price']:.2f}</div>
        <div class="{chg_cls}" style="text-align:right">
          {arrow} {sign}{d['change']:.2f}&nbsp;({sign}{d['change_pct']:.2f}%)
        </div>
      </div>
    </div>

    <div class="metrics">
      <div class="m">
        <div class="m-lbl">시가총액</div>
        <div class="m-val">{format_market_cap(d['market_cap'])}</div>
      </div>
      <div class="m">
        <div class="m-lbl">공매도 비율</div>
        <div class="m-val">{short_str}</div>
      </div>
      <div class="m">
        <div class="m-lbl">기관 보유율</div>
        <div class="m-val">{inst_str}</div>
      </div>
      <div class="m">
        <div class="m-lbl">거래량</div>
        <div class="m-val">{d['volume']:,}{vol_ratio}</div>
      </div>
      <div class="m">
        <div class="m-lbl">평균 거래량</div>
        <div class="m-val">{d['avg_volume']:,}</div>
      </div>
    </div>
"""

        # 뉴스
        news_list = news_data.get(d["ticker"], [])
        if news_list:
            html += f'    <div class="sec-title">📰 {d["ticker"]} 최신 뉴스</div>\n'
            for art in news_list:
                html += f"""    <div class="news-item">
      <a href="{art['link']}" class="news-a">{art['title']}</a>
      <div class="news-date">{art['published']}</div>
    </div>
"""
        html += "  </div>\n"  # card

    html += """  <div class="footer">
    이 이메일은 자동으로 생성되었습니다. 투자 결정은 본인의 판단으로 하세요.
  </div>
</div>
</body>
</html>"""
    return html


def send_email(html: str, subject: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())


def main():
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] 주식 데이터 수집 시작...")

    stocks_data, news_data = [], {}
    for ticker in TICKERS:
        print(f"  · {ticker} 데이터 수집 중...")
        try:
            stocks_data.append(get_stock_data(ticker))
            news_data[ticker] = get_news(ticker)
        except Exception as exc:
            print(f"  ! {ticker} 오류: {exc}")

    hour = now.hour
    session = "장 시작 전" if 12 <= hour < 18 else "장 마감"
    subject = (
        f"📈 [{session}] NVDA & PLTR 리포트 — "
        f"{now.strftime('%m/%d %H:%M')} (독일)"
    )

    html = build_html(stocks_data, news_data)

    print(f"  · 이메일 발송 중 → {RECEIVER_EMAIL}")
    send_email(html, subject)
    print("  ✓ 발송 완료!")


if __name__ == "__main__":
    main()
