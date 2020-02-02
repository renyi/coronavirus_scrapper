import os

try:
    import lxml  # noqa

    HTML_PARSER = "lxml"
except ImportError:
    try:
        import html5lib  # noqa

        HTML_PARSER = "html5lib"
    except ImportError:
        HTML_PARSER = "html.parser"

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB = os.getenv("DB")
NEWSAPI_TABLE = os.getenv("NEWSAPI_TABLE")

DEBUG = False

OFFLINE_MODE = False

KEYWORDS = (
    "冠状病毒",
    "武汉冠状病毒",
    "武漢冠狀病毒",
    "疫情",
    "wuhan coronavirus",
    "2019-nCoV",
    "novel coronavirus",
)

DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

PROXIES = {
    # "http": "http://127.0.0.1:3080",
    # "https": "http://127.0.0.1:3081",
}

# Enable/disable bots here.
BOTS = (
    "scrapper.bots.toutiao.CgtnToutiaoScrapper",
    "scrapper.bots.toutiao.Cctv4ToutiaoScrapper",
    "scrapper.bots.toutiao.CctvToutiaoScrapper",
    "scrapper.bots.toutiao.CctvQuickToutiaoScrapper",
    "scrapper.bots.toutiao.ChinaDailyToutiaoScrapper",
    "scrapper.bots.toutiao.ChinaYouthToutiaoScrapper",
    "scrapper.bots.toutiao.BeijingNewsToutiaoScrapper",
    "scrapper.bots.toutiao.EconomicDailyToutiaoScrapper",
    "scrapper.bots.toutiao.ChinaNewsToutiaoScrapper",
    "scrapper.bots.toutiao.PeopleDailyToutiaoScrapper",
    "scrapper.bots.toutiao.PeopleDailyOverseasToutiaoScrapper",
)

TOUTIAO_PAGE = 5
