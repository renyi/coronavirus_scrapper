import httpx
import abc
import json

from datetime import datetime


try:
    import lxml  # noqa

    HTML_PARSER = "lxml"
except ImportError:
    try:
        import html5lib  # noqa

        HTML_PARSER = "html5lib"
    except ImportError:
        HTML_PARSER = "html.parser"


KEYWORDS = ("冠状病毒", "武汉冠状病毒", "武漢冠狀病毒")

DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

PROXIES = {
    # "http": "http://127.0.0.1:3080",
    # "https": "http://127.0.0.1:3081",
}

client = httpx.AsyncClient(headers=DEFAULT_HEADERS, proxies=PROXIES)


class Scapper(abc.ABC):
    def save(self, data, filename=None):
        if filename is None:
            today = datetime.today()
            filename = f"{self.site_name}-{today.year}-{today.month}-{today.day}.json"

        data["timestamp"] = datetime.now().isoformat()

        with open(filename, "w") as outfile:
            json.dump(data, outfile)


def find_by_key(d, target):
    if isinstance(d, (dict, list, tuple)):
        for k, v in d.items():
            if isinstance(v, dict):
                yield from find_by_key(v, target)

            elif isinstance(v, (list, tuple)):
                for x in v:
                    yield from find_by_key(x, target)

            elif k == target:
                yield v
