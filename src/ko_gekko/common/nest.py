"""
nest.py:
Entrypoint class of the Kogekko library, handles multiple crawlers
"""

import concurrent.futures as futures
from ko_gekko.common.crawler import Crawler
from ko_gekko.common.error import KoGekkoBackendError
from requests import HTTPError
from requests_html import HTMLResponse
from typing import Optional, NamedTuple
from loguru import logger


class RetrievalResult(NamedTuple):
    url: str
    raw_data: bytes
    links: int
    images: int


logger.disable("ko_gekko")


class Nest:
    def __init__(self, max_threads: Optional[int]):
        try:
            self.crawler_pool: futures.ThreadPoolExecutor = futures.ThreadPoolExecutor(
                max_workers=max_threads
            )
            logger.success(
                f"Initiated KoGekko nest with {self.crawler_pool._max_workers}",
                "max crawlers",
            )
        except ValueError as err:
            logger.critical(f"Invalid ThreadPoolExecutor initialization: {err}")
            raise KoGekkoBackendError from err

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("Waiting for thread pool to shutdown...")
        self.crawler_pool.shutdown(wait=True, cancel_futures=True)
        logger.debug("Done")

    def retrieve_pages(
        self, urls: list[str]
    ) -> tuple[list[RetrievalResult], list[str]]:
        result: list[RetrievalResult] = []
        failed_urls: list[str] = []
        crawler_futures: dict[futures.Future, str] = {}

        try:
            for url in urls:
                crawler = Crawler(url)
                future = self.crawler_pool.submit(crawler.retrieve)
                logger.debug(f'Added crawler for url "{url}"')
                crawler_futures[future] = url
        except RuntimeError as err:
            logger.critical(
                f"Encountered an error while submitting a crawler thread: {err}"
            )
            raise KoGekkoBackendError from err

        try:
            for completed_crawler in futures.as_completed(
                crawler_futures, timeout=10.0
            ):
                url = crawler_futures[completed_crawler]

                try:
                    crawler_result: tuple[
                        HTMLResponse, int, int
                    ] = completed_crawler.result()
                    (response, links, images) = crawler_result
                    result.append(
                        RetrievalResult(url, response.html.raw_html, links, images)
                    )
                    logger.success(f'Successfully retrieved url "{url}"')
                except futures.CancelledError:
                    logger.warning('Crawler for url "{url}" was cancelled')
                    failed_urls.append(url)
                except HTTPError as err:
                    logger.warning(
                        f"Site returned the following HTTP error: {err.strerror}"
                    )
                except Exception as err:
                    failed_urls.append(url)
                    logger.error(f"Encountered error while retrieving {url}: {err}")
                    raise

        except futures.TimeoutError as err:
            logger.error(
                "Could not generate an iterator to the completed crawler threads!"
            )
            raise KoGekkoBackendError from err

        return (result, failed_urls)
