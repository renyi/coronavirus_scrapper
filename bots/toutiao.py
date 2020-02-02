#!/usr/bin/env python

import httpx
import asyncio
import re
import logging
import abc

from lxml.html.clean import clean_html
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse
from pyjsparser import parse as parse_js

from .settings import TOUTIAO_PAGE
from .base import Scapper
from .config import HTML_PARSER, KEYWORDS, DEFAULT_HEADERS, PROXIES

logger = logging.getLogger("scrapper")


class ToutiaoScrapper(Scapper, abc.ABC):
    site_name = "Toutiao"

    root = "https://m.toutiao.com/"
    endpoint = "https://www.toutiao.com/c/user/article/"
    timeout: int = 15

    user_id = None
    author = None

    def __init__(self):
        logger.info(f"{self}: Starting ...")

        if not self.user_id:
            raise Exception("user_id is not set.")

    def __str__(self):
        return self.__class__.__name__

    def parse_article(self, html_doc: str) -> dict:
        result = {}

        soup = BeautifulSoup(html_doc, HTML_PARSER)

        try:
            # Find articleInfo
            r = soup.body.findAll(text=re.compile("articleInfo"))[0]
        except KeyError:
            return None

        # Parse javascript
        # ArticleInfo should be in a script tag ..
        js = parse_js(r)

        # Find all "value" key
        value_list = [v for v in self.find_by_key(js, "value")]

        # Assume that the longest value is the content
        content_html = max([str(v) for v in value_list], key=len)
        content_html = clean_html(content_html)
        article_soup = BeautifulSoup(content_html, HTML_PARSER)
        result["content"] = article_soup.get_text()

        # Assume value with valid date is the date
        parsed_date = None
        for v in value_list:
            if v and isinstance(v, str):
                try:
                    parsed_date = parse(v, fuzzy=True)
                    if parsed_date is not None:
                        # Found the date we want
                        break
                except (ValueError, OverflowError):
                    # Not valid date
                    pass

        result["published"] = parsed_date

        return result

    async def run(self):  # noqa
        """
            https://www.toutiao.com/c/user/82615367134/#mid=1588042509127693
            https://www.toutiao.com/c/user/article/?page_type=1&user_id=82615367134
            https://www.toutiao.com/c/user/article/?page_type=1&user_id=82615367134&max_behot_time=1579098086

            https://www.toutiao.com/c/user/article/?page_type=1&user_id=82615367134&max_behot_time=0&count=20&as=A1B5BE13F218706&cp=5E3218C7D0863E1
            https://www.toutiao.com/c/user/article/?page_type=1&user_id=82615367134&max_behot_time=1579098086&count=20&as=A1C56EC322E93BE&cp=5E32E9F38B2EBE1

            params = {
                "page_type": 1,
                "user_id": 82615367134,
                "max_behot_time": 0,
                "count": 20,
                "as": "A1B5BE13F218706",
                "cp": "5E3218C7D0863E1",
            }
        """
        crawl = 0  # Crawl pagination depth
        max_behot_time = 0
        has_more = True

        client = self.client

        # Get cookie
        await client.get(
            f"https://www.toutiao.com/c/user/{self.user_id}/", timeout=self.timeout
        )

        while has_more is True:
            endpoint = f"{self.endpoint}?page_type=1&user_id={self.user_id}&max_behot_time={max_behot_time}"
            logger.info(f"{self}: {endpoint}")

            # Get a list of articles
            try:
                r = await client.get(endpoint, timeout=self.timeout)
            except httpx.exceptions.ConnectTimeout:
                pass

            result = None
            if r.status_code == 200:
                result = r.json()

                article_list = result.get("data")
                for article in article_list:
                    try:
                        title = article["title"]
                        description = article["abstract"]

                        title_lower = title.lower()
                        description_lower = description.lower()

                        # Check for keywords
                        if any(word in title_lower for word in KEYWORDS) or any(
                            word in description_lower for word in KEYWORDS
                        ):
                            article_url = f"{self.root}a{article['item_id']}"
                            logger.info(f"{self}: {article_url}")

                            try:
                                # Download article
                                r2 = await client.get(article_url, timeout=self.timeout)
                            except httpx.exceptions.ConnectTimeout:
                                pass

                            if r2.status_code == 200:
                                result2 = r2.text

                                try:
                                    parsed = self.parse_article(result2)
                                except Exception as e:
                                    logger.error(f"{self}: parse_article: {e}")

                                if parsed:
                                    data = {
                                        "title": article["title"],
                                        "description": description,
                                        "author": self.author,
                                        "url": article_url,
                                        "content": parsed.get("content"),
                                        "urlToImage": article.get("image_url", ""),
                                        "publishedAt": parsed.get("published").strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        ),
                                        "addedOn": datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        ),
                                        "siteName": self.site_name,
                                        "language": "zh",
                                    }
                                    self.data_list.append(data)

                        await asyncio.sleep(1)

                    except Exception as e:
                        logger.error(f"{self}: {e}")

            if result:
                # Pagination
                has_more = result.get("has_more", False)
                logger.debug(f"{self}: has_more: {has_more}")

                if has_more is True:
                    try:
                        max_behot_time = result.get("next")["max_behot_time"]
                    except KeyError:
                        logger.error(f"{self}: max_behot_time missing.")
                else:
                    has_more = False

                crawl += 1
                logger.debug(f"{self}: crawl: {crawl}")

                if crawl > TOUTIAO_PAGE:
                    break

                await asyncio.sleep(1)

        await self.save_db()
        # await self.save_file()


class CgtnToutiaoScrapper(ToutiaoScrapper):
    user_id = "82615367134"  # toutiao userid
    author = ""
    site_name = "CGTN Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class Cctv4ToutiaoScrapper(ToutiaoScrapper):
    user_id = "5834354287"  # toutiao userid
    author = ""
    site_name = "Cctv4 Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class CctvToutiaoScrapper(ToutiaoScrapper):
    user_id = "4492956276"  # toutiao userid
    author = ""
    site_name = "CCTV News Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class CctvQuickToutiaoScrapper(ToutiaoScrapper):
    user_id = "99138739220"  # toutiao userid
    author = ""
    site_name = "CCTV quick review Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class ChinaDailyToutiaoScrapper(ToutiaoScrapper):
    user_id = "3430213523"  # toutiao userid
    author = ""
    site_name = "China Daily Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class ChinaYouthToutiaoScrapper(ToutiaoScrapper):
    user_id = "3582660809"  # toutiao userid
    author = ""
    site_name = "China Youth Network Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class BeijingNewsToutiaoScrapper(ToutiaoScrapper):
    user_id = "5540918998"  # toutiao userid
    author = ""
    site_name = "Beijing News Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class EconomicDailyToutiaoScrapper(ToutiaoScrapper):
    user_id = "50098460684"  # toutiao userid
    author = ""
    site_name = "Economic daily Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class ChinaNewsToutiaoScrapper(ToutiaoScrapper):
    user_id = "5140856177"  # toutiao userid
    author = ""
    site_name = "China News Weekly Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class PeopleDailyToutiaoScrapper(ToutiaoScrapper):
    user_id = "5722070530"  # toutiao userid
    author = ""
    site_name = "People's Daily Review Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class PeopleDailyOverseasToutiaoScrapper(ToutiaoScrapper):
    user_id = "3242684112"  # toutiao userid
    author = ""
    site_name = "People's Daily Overseas Website Toutiao"
    client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)
