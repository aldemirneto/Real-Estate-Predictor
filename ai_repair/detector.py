"""
Detects broken scrapers by running each one and checking for failures or empty results.
Returns a list of (scraper_name, error_message, sample_html) tuples.
"""
import importlib
import traceback

import requests

from config.ConfigManager import ConfigManager
from Log.Logging import Logging


class ScraperDetector:
    _UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    def __init__(self):
        self.config = ConfigManager().get_config()
        self.log = Logging()

    def _fetch_sample_html(self, url: str) -> str:
        try:
            r = requests.get(url, headers={"User-Agent": self._UA}, timeout=30)
            return r.text
        except Exception:
            return ""

    def check_scraper(self, name: str) -> tuple[bool, str, str]:
        """
        Returns (is_broken, error_message, sample_html).
        A scraper is considered broken if it raises an exception or returns 0 results.
        """
        cfg = self.config["websites"].get(name, {})
        sample_url = cfg.get("url", "") + "1"
        sample_html = self._fetch_sample_html(sample_url)

        try:
            module = importlib.import_module(f"Extract.{name}Scraper")
            cls = getattr(module, f"{name}Scraper")
            instance = cls()
            data = instance.scrape()
            if not data:
                return True, "Scraper returned 0 results", sample_html
            return False, "", sample_html
        except Exception:
            return True, traceback.format_exc(), sample_html

    def find_broken(self) -> list[tuple[str, str, str]]:
        """Check all active scrapers and return the broken ones."""
        broken = []
        for name, cfg in self.config["websites"].items():
            if not cfg.get("Ativo"):
                continue
            self.log.log(f"Checking {name}...")
            is_broken, error, html = self.check_scraper(name)
            if is_broken:
                self.log.log(f"BROKEN: {name} — {error[:120]}")
                broken.append((name, error, html))
            else:
                self.log.log(f"OK: {name}")
        return broken
