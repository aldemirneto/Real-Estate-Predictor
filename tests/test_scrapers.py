"""
Tests for individual scraper parse_page methods.

Strategy: instantiate scrapers bypassing __init__ (no HTTP, no config I/O),
inject a real HTML fixture into raw_websites, then run parse_page and assert
the resulting raw_data has the expected shape.
"""
import pytest
from unittest.mock import patch, MagicMock

from Extract.DuoScraper import DuoScraper
from Extract.JunqueiraScraper import JunqueiraScraper
from Extract.AtoScraper import AtoScraper
from Extract.PremierScraper import PremierScraper
from Extract.MiguelScraper import MiguelScraper
from Log.Logging import Logging

REQUIRED_KEYS = {"preco", "area", "quartos", "vagas", "banheiros", "bairro", "tipo", "Status", "link", "Imobiliaria"}


def _bare_scraper(cls):
    """Create a scraper instance without calling __init__."""
    obj = object.__new__(cls)
    obj.raw_data = []
    obj.raw_websites = []
    obj.Log = MagicMock(spec=Logging)
    return obj


def _assert_valid_properties(raw_data, min_count=1):
    assert len(raw_data) >= min_count, f"Expected at least {min_count} properties, got {len(raw_data)}"
    for prop in raw_data:
        assert REQUIRED_KEYS.issubset(prop.keys()), f"Missing keys: {REQUIRED_KEYS - prop.keys()}"
        assert prop["Status"] == "Compra"
        assert isinstance(prop["link"], str) and prop["link"].startswith("http")
        if prop["preco"] is not None:
            assert isinstance(prop["preco"], float), f"preco should be float, got {type(prop['preco'])}"


# ── Duo ──────────────────────────────────────────────────────────────────────

class TestDuoScraper:
    def test_parse_page_extracts_properties(self, duo_page):
        scraper = _bare_scraper(DuoScraper)
        scraper.raw_websites = [duo_page]
        scraper.parse_page()
        _assert_valid_properties(scraper.raw_data, min_count=5)

    def test_parse_page_all_have_price(self, duo_page):
        scraper = _bare_scraper(DuoScraper)
        scraper.raw_websites = [duo_page]
        scraper.parse_page()
        prices = [p["preco"] for p in scraper.raw_data]
        assert all(isinstance(p, float) for p in prices)

    def test_parse_page_imobiliaria_name(self, duo_page):
        scraper = _bare_scraper(DuoScraper)
        scraper.raw_websites = [duo_page]
        scraper.parse_page()
        assert all(p["Imobiliaria"] == "Duo_imoveis" for p in scraper.raw_data)

    def test_parse_page_clears_raw_websites(self, duo_page):
        scraper = _bare_scraper(DuoScraper)
        scraper.raw_websites = [duo_page]
        scraper.parse_page()
        assert scraper.raw_websites == []

    def test_parse_page_prices_are_positive(self, duo_page):
        scraper = _bare_scraper(DuoScraper)
        scraper.raw_websites = [duo_page]
        scraper.parse_page()
        assert all(p["preco"] > 0 for p in scraper.raw_data)


# ── Junqueira ────────────────────────────────────────────────────────────────

class TestJunqueiraScraper:
    def test_parse_page_extracts_properties(self, junqueira_page):
        scraper = _bare_scraper(JunqueiraScraper)
        # Junqueira parse_page expects list-of-soups (it flattens Tags)
        scraper.raw_websites = [[junqueira_page]]
        scraper.parse_page()
        _assert_valid_properties(scraper.raw_data, min_count=5)

    def test_parse_page_imobiliaria_name(self, junqueira_page):
        scraper = _bare_scraper(JunqueiraScraper)
        scraper.raw_websites = [[junqueira_page]]
        scraper.parse_page()
        assert all(p["Imobiliaria"] == "Junqueira" for p in scraper.raw_data)

    def test_parse_page_clears_raw_websites(self, junqueira_page):
        scraper = _bare_scraper(JunqueiraScraper)
        scraper.raw_websites = [[junqueira_page]]
        scraper.parse_page()
        assert scraper.raw_websites == []


# ── Ato ──────────────────────────────────────────────────────────────────────

class TestAtoScraper:
    def test_parse_page_extracts_properties(self, ato_page):
        scraper = _bare_scraper(AtoScraper)
        scraper.raw_websites = [ato_page]
        scraper.parse_page()
        _assert_valid_properties(scraper.raw_data, min_count=1)

    def test_parse_page_imobiliaria_name(self, ato_page):
        scraper = _bare_scraper(AtoScraper)
        scraper.raw_websites = [ato_page]
        scraper.parse_page()
        assert all(p["Imobiliaria"] == "Ato" for p in scraper.raw_data)

    def test_parse_page_prices_are_floats(self, ato_page):
        scraper = _bare_scraper(AtoScraper)
        scraper.raw_websites = [ato_page]
        scraper.parse_page()
        for prop in scraper.raw_data:
            if prop["preco"] is not None:
                assert isinstance(prop["preco"], float)


# ── Premier ──────────────────────────────────────────────────────────────────

class TestPremierScraper:
    def test_parse_page_extracts_properties(self, premier_page):
        scraper = _bare_scraper(PremierScraper)
        scraper.raw_websites = [premier_page]
        scraper.parse_page()
        _assert_valid_properties(scraper.raw_data, min_count=5)

    def test_parse_page_bairro_from_url(self, premier_page):
        scraper = _bare_scraper(PremierScraper)
        scraper.raw_websites = [premier_page]
        scraper.parse_page()
        for prop in scraper.raw_data:
            assert prop["bairro"] != "Sem Bairro", "bairro should be extracted from URL"
            assert "-" not in prop["bairro"], "URL slugs should be converted to spaces"

    def test_parse_page_imobiliaria_name(self, premier_page):
        scraper = _bare_scraper(PremierScraper)
        scraper.raw_websites = [premier_page]
        scraper.parse_page()
        assert all(p["Imobiliaria"] == "Premier_imoveis" for p in scraper.raw_data)


# ── Miguel ───────────────────────────────────────────────────────────────────

class TestMiguelScraper:
    def test_parse_page_extracts_properties(self, miguel_page):
        scraper = _bare_scraper(MiguelScraper)
        scraper.raw_websites = [miguel_page]
        scraper.parse_page()
        _assert_valid_properties(scraper.raw_data, min_count=1)

    def test_parse_page_imobiliaria_name(self, miguel_page):
        scraper = _bare_scraper(MiguelScraper)
        scraper.raw_websites = [miguel_page]
        scraper.parse_page()
        assert all(p["Imobiliaria"] == "Miguel_imoveis" for p in scraper.raw_data)

    def test_parse_page_skips_properties_without_price(self, miguel_page):
        scraper = _bare_scraper(MiguelScraper)
        scraper.raw_websites = [miguel_page]
        scraper.parse_page()
        assert all(isinstance(p["preco"], float) for p in scraper.raw_data)
