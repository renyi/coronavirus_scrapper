import httpx
import asyncio
import re

from bs4 import BeautifulSoup
from datetime import datetime
from pyjsparser import parse as parse_js

from base import KEYWORDS, HTML_PARSER, Scapper, client, find_by_key


class CgtnScrapper(Scapper):
    __author__ = "Renyi Khor"
    __email__ = "renyi.ace@gmail.com"
    __copyright__ = "Copyright 2020, The Coronavirus Tracker Scrapper"

    site_name = "CGTN toutiao"

    root = "https://m.toutiao.com/"
    endpoint = "https://www.toutiao.com/c/user/article/"
    timeout: int = 15

    user_id = "82615367134"  # cgtn userid
    max_crawl = 5  # Infinite pagination

    def parse_article(self, html_doc):
        from dateutil.parser import parse

        result = {}

        soup = BeautifulSoup(html_doc, HTML_PARSER)

        # Parse javascript
        r = soup.body.findAll(text=re.compile("articleInfo"))[0]

        # ArticleInfo should be in a script tag ..
        js = parse_js(r)

        value_list = [v for v in find_by_key(js, "value")]

        # Assume that the longest value is the content
        content_html = max([str(v) for v in value_list], key=len)
        article_soup = BeautifulSoup(content_html, HTML_PARSER)
        result["content"] = article_soup.get_text()

        # Assume value with valid date is the date
        parsed_date = None
        for v in value_list:
            if v and isinstance(v, str):
                try:
                    parsed_date = parse(v, fuzzy=True)
                    if parsed_date is not None:
                        parsed_date = parsed_date.isoformat()
                        break
                except (ValueError, OverflowError):
                    # Not valid date
                    pass

        result["published"] = parsed_date

        return result

    async def run(self):
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

        max_behot_time = 0

        endpoint = f"{self.endpoint}?page_type=1&user_id={self.user_id}&max_behot_time={max_behot_time}"

        # Get login cookie
        await client.get(
            "https://www.toutiao.com/c/user/82615367134/", timeout=self.timeout
        )

        # Get a list of articles
        r = await client.get(endpoint, timeout=self.timeout)

        if r.status_code == 200:
            result = r.json()

            data_list = []

            article_list = result.get("data")
            print(len(article_list))

            for article in article_list:
                title = article["title"]
                description = article["abstract"]
                print(title)

                # Check for keywords
                if any(word in title for word in KEYWORDS) or any(
                    word in description for word in KEYWORDS
                ):
                    article_url = f"{self.root}a{article['item_id']}"

                    try:
                        # Download article
                        r2 = await client.get(article_url, timeout=self.timeout)

                        if r2.status_code == 200:
                            result2 = r2.text

                            parsed = self.parse_article(result2)

                            data = {
                                "title": article["title"],
                                "description": description,
                                "author": "",
                                "url": article_url,
                                "content": parsed.get("content"),
                                "urlToImage": article["image_url"],
                                "publishedAt": parsed.get("published"),
                                "addedOn": datetime.now().isoformat(),
                                "siteName": self.site_name,
                                "language": "zh",
                            }

                            data_list.append(data)

                    except httpx.exceptions.ConnectTimeout:
                        continue

                await asyncio.sleep(1)

            # TODO: Pagination
            # has_more = result.get("has_more")
            # if has_more is True:
            #     max_behot_time = result.get("next")["max_behot_time"]

            # else:
            #     break

            self.save({"data": data_list})


async def main():
    s = CgtnScrapper()
    await s.run()


if __name__ == "__main__":
    asyncio.run(main())
