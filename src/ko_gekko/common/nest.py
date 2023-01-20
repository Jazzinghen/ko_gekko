"""
nest.py:
Entrypoint class of the Kogekko library, handles multiple crawlers
"""

import concurrent.futures
from datetime import datetime

RetrievalResult = tuple[int, int, datetime]


class Nest:
    def __init__(self, max_threads: int | None):
        self.crawler_pool: concurrent.futures.ThreadPoolExecutor = (
            concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)
        )

    def retrieve_pages(self, urls: list[str]) -> list[RetrievalResult]:

        return []
