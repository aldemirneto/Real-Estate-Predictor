import requests
from bs4 import BeautifulSoup

import concurrent.futures

from Log.Logging import Logging


class BaseScraper:
    def __init__(self):
        loging = Logging()
        self.Log = loging
        self.step = 1
        self.raw_data = []
        self.raw_websites = []
        self.websites = None
        self.website_path = None
        self.breakpoint = None

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def set_breakpoint(self):
        pass

    def get_page_content(self, request_url):
        try:
            page_response = self.session.get(request_url, timeout=30, allow_redirects=False)
            if page_response.status_code == 200:
                return BeautifulSoup(page_response.content, "html.parser")

        except requests.RequestException as e:
            self.Log.error(f"Error fetching {request_url}: {e}")
            return None

    def fetch_page(self):
        if not self.breakpoint:
            self.set_breakpoint()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self.get_page_content, f'{self.website_path}{i}'): i
                for i in range(0, self.breakpoint, self.step)
            }
            for future in concurrent.futures.as_completed(future_to_url):
                if future.result():
                    self.raw_websites.append(future.result())


    def parse_page(self):
        pass

    def scrape(self):
        self.set_breakpoint()
        self.fetch_page()
        self.parse_page()

        return self.raw_data
