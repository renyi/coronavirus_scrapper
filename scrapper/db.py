import aiomysql
import asyncio
import logging

import scrapper.settings

pool = None

loop = asyncio.get_event_loop()

logger = logging.getLogger("scrapper")


async def get_dbpool():
    global pool

    if pool is None:
        pool = await aiomysql.create_pool(
            host=scrapper.settings.DB_HOST,
            port=scrapper.settings.DB_PORT,
            user=scrapper.settings.DB_USER,
            password=scrapper.settings.DB_PASSWORD,
            db=scrapper.settings.DB,
            loop=loop,
            autocommit=False,
        )

    return pool


async def write_db(data_list: list, commit: bool = False):
    if data_list:
        db_pool = await get_dbpool()
        async with db_pool.acquire() as conn:
            values_list = []

            for data in data_list:
                columns = ",".join(data.keys())
                values = ",".join(["%s" for v in data.values()])

                stmt1 = f"INSERT INTO `{scrapper.settings.NEWSAPI_TABLE}` ({columns}) VALUES ({values})"
                stmt2 = f"ON DUPLICATE KEY UPDATE siteName='{data['siteName']}', author='{data['author']}', publishedAt='{data['publishedAt']}', addedOn='{data['addedOn']}'"

                stmt = f"{stmt1} {stmt2}"
                logger.debug(f"write_db: {stmt}")

                values_list.append(list(data.values()))

            if values_list:
                try:
                    async with conn.cursor() as cur:
                        for v in values_list:
                            await cur.execute(stmt, v)
                        await conn.commit()
                except Exception as e:
                    logger.error(e)
