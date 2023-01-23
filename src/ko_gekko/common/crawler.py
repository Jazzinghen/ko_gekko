"""
crawler.py:
A single internet crawler
"""

import requests_html
from loguru import logger


class Crawler:
    def __init__(self, url: str):
        self.url = url

    def retrieve(self) -> tuple[requests_html.HTMLResponse, int, int]:
        session: requests_html.HTMLSession = requests_html.HTMLSession()
        response: requests_html.HTMLResponse = session.get(self.url)
        link_qty: int = len(response.html.links)
        picture_qty: int = len(response.html.find("img"))

        return (response, link_qty, picture_qty)
