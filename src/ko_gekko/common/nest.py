"""
nest.py:
Entrypoint class of the Kogekko library, handles multiple crawlers
"""

import concurrent.futures
from datetime import datetime
import sqlite3 as sl
import platformdirs
from pathlib import Path
import validators
from ko_gekko.common.crawler import Crawler

RetrievalResult = tuple[str, int, int, datetime]


class Nest:
    def __init__(self, max_threads: int | None):
        self.crawler_pool: concurrent.futures.ThreadPoolExecutor = (
            concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)
        )
        nest_data_root: Path = platformdirs.user_data_path(
            "Kogekko", "Jazzinghen", roaming=True
        )

        nest_database_path: Path = nest_data_root / "fetch.db"

        self.database_connection: sl.Connection = sl.connect(nest_database_path)

        nest_table_query: str = """ CREATE TABLE IF NOT EXISTS "fetch_times"
        (
            [PageId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [PageUrl] TEXT UNIQUE  NOT NULL,
            [LastTimestamp] INTEGER NOT NULL,
        ) STRICT;
        """

        with self.database_connection:
            self.database_connection.execute(nest_table_query)
            table_check = self.database_connection.execute(
                "SELECT name FROM sqlite_master"
            )
            table_check.fetchone()
            assert "fetch_times" in table_check

    def retrieve_pages(self, urls: list[str]) -> list[RetrievalResult]:
        result: list[RetrievalResult] = []
        crawler_futures: dict[concurrent.futures.Future, str] = {}

        for url in urls:
            validation: bool | validators.ValidationFailure = validators.url(url)
            if validation is not True:
                raise validation
            crawler = Crawler(url)
            future = self.crawler_pool.submit(crawler.retrieve)
            crawler_futures[future] = url

        for completed_crawler in concurrent.futures.as_completed(crawler_futures):
            url = crawler_futures[completed_crawler]
            try:
                (response, links, images) = completed_crawler.result()
                result.append((url, links, images, datetime.min))
            except Exception as err:
                print(f"Encountered error while retrieving {url}: {err}")

        return result
