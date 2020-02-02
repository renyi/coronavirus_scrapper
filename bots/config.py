try:
    import lxml  # noqa

    HTML_PARSER = "lxml"
except ImportError:
    try:
        import html5lib  # noqa

        HTML_PARSER = "html5lib"
    except ImportError:
        HTML_PARSER = "html.parser"

DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

PROXIES = {
    # "http": "http://127.0.0.1:3080",
    # "https": "http://127.0.0.1:3081",
}

KEYWORDS = (
    "冠状病毒",
    "武汉冠状病毒",
    "武漢冠狀病毒",
    "疫情",
    "wuhan coronavirus",
    "2019-nCoV",
    "novel coronavirus",
)
