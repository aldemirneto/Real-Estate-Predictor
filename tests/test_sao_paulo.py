from pathlib import Path
from unittest.mock import Mock
from bs4 import BeautifulSoup
from Extract.SaoPauloScraper import LopesLTScraper
from Extract.LopesRTGScraper import LopesRTGScraper
from Transform.DataCleaner import DataCleaner

FIXTURES = Path(__file__).parent / "fixtures/html"


def test_lt_prices_areas_and_city():
    scraper = LopesLTScraper()
    scraper.raw_websites = [BeautifulSoup((FIXTURES / "lopes_lt.html").read_text(), "html.parser")]
    scraper.parse_page()
    assert scraper.raw_data[0]["preco"] == 603000
    assert scraper.raw_data[0]["area"] == 180
    assert scraper.raw_data[0]["bairro"] == "Vila Marieta"
    assert all(p["cidade"] == "São Paulo" for p in scraper.raw_data)
    assert scraper.raw_data[0]["banheiros"] is None


def test_repeated_pages_preserve_first_page(monkeypatch):
    scraper = LopesLTScraper()
    page = BeautifulSoup((FIXTURES / "lopes_lt.html").read_text(), "html.parser")
    scraper.get_page_content = Mock(return_value=page)
    monkeypatch.setattr("Extract.SaoPauloScraper.time.sleep", lambda _: None)
    rows = scraper.scrape()
    assert len(rows) == len({p["link"] for p in rows}) == 2


def test_rtg_sale_details_not_similar_properties():
    scraper = LopesRTGScraper()
    page = BeautifulSoup((FIXTURES / "lopes_rtg.html").read_text(), "html.parser")
    scraper.parse_detail(page, "https://www.lopesrtg.com.br/imovel/REO270749/")
    assert len(scraper.raw_data) == 1
    assert scraper.raw_data[0]["preco"] == 3500000
    assert scraper.raw_data[0]["area"] == 186.96
    assert scraper.raw_data[0]["vagas"] == 2
    assert scraper.raw_data[0]["cidade"] == "São Paulo"


def test_sp_parque_neighborhood_is_retained():
    rows = DataCleaner([[{"bairro": "Parque São Domingos", "cidade": "São Paulo"}, {"bairro": "Centro"}]]).validate_data()
    assert rows[0]["bairro"] == "Parque_sao_domingos"
    assert rows[1]["cidade"] == "Piracicaba"
