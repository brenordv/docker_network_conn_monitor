# -*- coding: utf-8 -*-
from os import path
from os import environ

TEST_SITE_LIST = [
    "https://www.google.com",
    "https://www.duckduckgo.com",
    "https://www.cloudflare.com/",
    "https://www.bing.com"
]

DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
}

DATABASE_FILE = path.join(path.abspath(path.dirname(__file__)), "./statistics.db")

try:
    SECONDS_BETWEEN_CHECKS = int(environ.get("SECONDS_BETWEEN_CHECKS", 60))
except:
    SECONDS_BETWEEN_CHECKS = 60

TELEGRAM_BOT_TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = environ.get("TELEGRAM_CHAT_ID")

try:
    STATISTICS_API_PORT = int(environ.get("STATISTICS_API_PORT", 10044))
except:
    STATISTICS_API_PORT = 10044

STATISTICS_API_HOST = environ.get("STATISTICS_API_HOST", "0.0.0.0")
