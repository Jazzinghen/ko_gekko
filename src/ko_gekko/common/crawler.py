# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
""" KoGekko's Crawler

A page crawler tasked to retrieve pages and parse their contents
"""

from loguru import logger
import requests_html


@logger.catch
class Crawler:
    """Page Crawler

    Attributes
    ----------
    url : str
        URL to the page to handle
    """

    def __init__(self, url: str):
        self.url = url

    def retrieve(self) -> tuple[requests_html.HTMLResponse, int, int]:
        """Retrieve the page provided at creation and parse its contents

        Returns
        -------
        tuple of requests_html.HTMLResponse and int and int
            A tuple containing the full HTML response from the page for further
            analysis, the amount of links in the requested page and the amount of
            images in the requested page

        Raises
        ------
        requests.HTTPError
            If the URL requested returned an error state when retrieving the page
        """
        logger.debug(f"Creating new HTML Session to download {self.url}")
        session: requests_html.HTMLSession = requests_html.HTMLSession()
        response: requests_html.HTMLResponse = session.get(self.url)  # type: ignore
        response.raise_for_status()

        logger.debug(f"Retrieved page {response.url}")
        link_qty: int = len(response.html.links)
        picture_qty: int = len(response.html.find("img"))  # type: ignore

        return (response, link_qty, picture_qty)
