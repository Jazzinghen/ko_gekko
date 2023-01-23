"""
nest.py:
Entrypoint class of the Kogekko library, handles multiple crawlers
"""

import concurrent.futures
from ko_gekko.common.crawler import Crawler
from typing import Optional
from loguru import logger
from collections import namedtuple

RetrievalResult = namedtuple("RetrievalResult", ["url", "raw_data", "links", "images"])
logger.disable("ko_gekko")


class Nest:
    def __init__(self, max_threads: Optional[int]):
        self.crawler_pool: concurrent.futures.ThreadPoolExecutor = (
            concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.crawler_pool.shutdown(wait=True, cancel_futures=True)

    def retrieve_pages(
        self, urls: list[str]
    ) -> tuple[list[RetrievalResult], list[str]]:
        result: list[RetrievalResult] = []
        crawler_futures: dict[concurrent.futures.Future, str] = {}

        failed_urls: list[str] = []

        for url in urls:
            crawler = Crawler(url)
            future = self.crawler_pool.submit(crawler.retrieve)
            crawler_futures[future] = url

        for completed_crawler in concurrent.futures.as_completed(crawler_futures):
            url = crawler_futures[completed_crawler]

            try:
                (response, links, images) = completed_crawler.result()
                result.append(
                    RetrievalResult(url, response.html.raw_html, links, images)
                )
            except Exception as err:
                failed_urls.append(url)
                print(f"Encountered error while retrieving {url}: {err}")

        return (result, failed_urls)
