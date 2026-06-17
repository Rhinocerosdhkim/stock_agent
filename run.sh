#!/bin/bash
# cron 실행용 래퍼 스크립트
cd "$(dirname "$0")"
python3 stock_agent.py
