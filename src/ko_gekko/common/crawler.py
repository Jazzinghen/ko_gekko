"""
crawler.py:
A single internet crawler
"""

import requests_html
import requests


class Crawler:
    def __init__(self, url: str):
        self.url = url

    def retrieve(self) -> tuple[requests.Response, int, int]:
        session: requests_html.HTMLSession = requests_html.HTMLSession()
        response: requests_html.HTMLResponse = session.get(self.url)
        link_qty: int = len(response.html.find("a:any-link"))
        picture_qty: int = len(response.html.find("img"))

        return (response, link_qty, picture_qty)
