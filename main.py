#!/usr/bin/env python

import asyncio
import uvloop
import logging

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger("scrapper")

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

f_handler = logging.FileHandler("logs/scappers.log")
f_handler.setLevel(logging.INFO)
f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)


async def main():
    from bots.toutiao import (
        cgtntoutiao_scrapper,
        cctv4toutiao_scrapper,
        cctvtoutiao_scrapper,
        cctvquicktoutiao_scrapper,
        chinadailytoutiao_scrapper,
        chinayouthtoutiao_scrapper,
        beijingnewstoutiao_scrapper,
        economicdailytoutiao_scrapper,
        chinanewstoutiao_scrapper,
        peopledailytoutiao_scrapper,
        peopledailyoverseastoutiao_scrapper,
    )

    await asyncio.gather(
        cgtntoutiao_scrapper.run(),
        cctv4toutiao_scrapper.run(),
        cctvtoutiao_scrapper.run(),
        cctvquicktoutiao_scrapper.run(),
        chinadailytoutiao_scrapper.run(),
        chinayouthtoutiao_scrapper.run(),
        beijingnewstoutiao_scrapper.run(),
        economicdailytoutiao_scrapper.run(),
        chinanewstoutiao_scrapper.run(),
        peopledailytoutiao_scrapper.run(),
        peopledailyoverseastoutiao_scrapper.run(),
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    asyncio.run(main())
