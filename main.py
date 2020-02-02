#!/usr/bin/env python


import asyncio
import uvloop
import logging
import logging.handlers

import scrapper.settings
import scrapper.utils

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger("scrapper")

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

# f_handler = logging.FileHandler("logs/scappers.log")
f_handler = logging.handlers.TimedRotatingFileHandler(
    "logs/scappers.log", backupCount=10, when="D"
)
f_handler.setLevel(logging.INFO)
f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)


async def main():
    task_list = [scrapper.utils.import_string(b) for b in scrapper.settings.BOTS]

    await asyncio.gather(*[T().run() for T in task_list])


if __name__ == "__main__":
    logging.getLogger().setLevel(
        logging.DEBUG if scrapper.settings.DEBUG is True else logging.INFO
    )

    asyncio.run(main())
