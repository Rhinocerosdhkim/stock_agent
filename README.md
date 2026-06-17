# Stock Agent

관심 종목(**NVDA**, **PLTR**)의 시세·지표·뉴스를 수집해
**HTML 리포트 이메일**을 자동 발송하는 모니터링 에이전트입니다.
cron으로 장 시작 전 / 장 마감 시각에 맞춰 자동 실행하도록 설계했습니다.

## 기능

- **시세 & 지표** — 현재가, 등락률, 시가총액, 공매도 비율, 기관 보유율, 거래량(평균 대비 배수)
- **뉴스** — Google News RSS에서 종목별 최신 기사 수집
- **리포트** — 반응형 HTML 카드 형태의 이메일 (모바일 대응)
- **자동 발송** — Gmail SMTP(SSL)로 지정 수신자에게 발송
- **스케줄링** — 독일 현지시각 기준 장 시작 전 / 장 마감 자동 실행

## 설치

```bash
pip install -r requirements.txt
```

## 설정

`.env.example`를 복사해 `.env`를 만들고 본인 값을 채웁니다.

```bash
cp .env.example .env
```

```dotenv
SENDER_EMAIL=your_sender@gmail.com
RECEIVER_EMAIL=your_receiver@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password   # Gmail 2단계 인증 후 발급한 앱 비밀번호
```

> `GMAIL_APP_PASSWORD`는 일반 계정 비밀번호가 아니라
> [Google 앱 비밀번호](https://myaccount.google.com/apppasswords)입니다.

## 실행

```bash
python3 stock_agent.py   # 수동 실행
./run.sh                 # cron 래퍼 스크립트
```

### cron 등록 예시

```cron
# 장 시작 전 (독일 14:00) / 장 마감 (독일 22:00)
0 14 * * 1-5 /path/to/stock_agent/run.sh >> /path/to/stock_agent/cron.log 2>&1
0 22 * * 1-5 /path/to/stock_agent/run.sh >> /path/to/stock_agent/cron.log 2>&1
```

## 기술 스택

- **yfinance** — 시세·지표 데이터
- **feedparser** — Google News RSS 파싱
- **smtplib / email** — Gmail SMTP 발송
- **pytz** — 타임존 처리

> ⚠️ 모니터링 목적의 도구이며 투자 자문이 아닙니다. 투자 결정은 본인의 판단으로 하세요.
