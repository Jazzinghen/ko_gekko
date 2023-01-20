"""
crawler.py:
A single internet crawler
"""

from bs4 import BeautifulSoup
import urllib.request


class Crawler:
    def __init__(self, name):
        self.name = name
