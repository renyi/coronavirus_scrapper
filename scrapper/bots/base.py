import abc
import orjson
import logging
import aiofile
import httpx
import asyncio

from datetime import datetime

from scrapper.db import write_db

logger = logging.getLogger("scrapper")


class Scapper(abc.ABC):
    client = None
    data_list = []

    def __str__(self):
        return self.__class__.__name__

    async def get(self, *args, **kwargs):
        # Get cookie
        try:
            r = await self.client.get(timeout=self.timeout, *args, **kwargs)
            await asyncio.sleep(1)
        except (httpx.exceptions.ConnectTimeout, httpx.exceptions.ReadTimeout):
            return None
        return r

    def find_by_key(self, d, target):
        if isinstance(d, (dict, list, tuple)):
            for k, v in d.items():
                if isinstance(v, dict):
                    yield from self.find_by_key(v, target)

                elif isinstance(v, (list, tuple)):
                    for x in v:
                        yield from self.find_by_key(x, target)

                elif k == target:
                    yield v

    async def save_file(self, filename=None):
        if self.data_list:
            now = datetime.utcnow().isoformat()

            data = {"data": self.data_list, "timestamp": now}

            if filename is None:
                filename = f"{self.site_name}-{now}.json"

            logger.debug(f"{self}: Saving {filename}")

            async with aiofile.AIOFile(f"data/{filename}", "w+") as afp:
                data = orjson.dumps(data)
                await afp.write(data.decode("utf-8"))
                await afp.fsync()

            logger.debug(f"{self}: Saved.")

    async def save_db(self):
        if self.data_list:
            logger.debug(f"{self}: Writing to db ..")
            await write_db(self.data_list)
            logger.debug(f"{self}: Done.")
