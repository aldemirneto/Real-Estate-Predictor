from pathlib import Path
from unittest.mock import MagicMock

import pytest
from bs4 import BeautifulSoup

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "html"

MOCK_CONFIG = {
    "websites": {
        "Duo":      {"url": "https://www.duoimoveis.com.br/imoveis/a-venda/piracicaba?pagina=", "step": 1, "Ativo": True},
        "Junqueira":{"url": "https://www.imobiliariajunqueira.com.br/comprar/todas?page=",     "step": 1, "Ativo": True},
        "Ato":      {"url": "https://imobiliariaato.com.br/imovel/venda?pagina=",               "step": 1, "Ativo": True},
        "Premier":  {"url": "https://premierimoveispiracicaba.com.br/imoveis/pagina-",          "step": 1, "Ativo": True},
        "Miguel":   {"url": "https://miguelimoveis.com.br/venda/residencial/",                  "step": 1, "Ativo": True},
        "FriasNeto":{"url": "https://www.friasneto.com.br/imoveis/todos-os-imoveis/?pag=",      "step": 1, "Ativo": True},
    },
    "BlackList": ["condominio", "chacara", "conjunto", "edificio", "convivio", "residencial",
                  "vivendas", "terra", "recanto", "loteamento", "-", "park", "parque", "nucleo"],
    "database": {},
    "other_settings": {"Periodicity": 24, "Log_file": "log.txt", "log_level": "INFO", "max_retries": 3},
    "remetente": {},
}


def _load_fixture(name: str) -> BeautifulSoup:
    html = (FIXTURES_DIR / f"{name}_page1.html").read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


@pytest.fixture
def mock_config(monkeypatch):
    """Patches ConfigManager so scrapers never touch config.json on disk."""
    mock_cm = MagicMock()
    mock_cm.return_value.get_config.return_value = MOCK_CONFIG
    monkeypatch.setattr("config.ConfigManager.ConfigManager", mock_cm)
    return MOCK_CONFIG


# ---------- per-scraper page fixtures ----------

@pytest.fixture
def duo_page():
    return _load_fixture("duo")

@pytest.fixture
def junqueira_page():
    return _load_fixture("junqueira")

@pytest.fixture
def ato_page():
    return _load_fixture("ato")

@pytest.fixture
def premier_page():
    return _load_fixture("premier")

@pytest.fixture
def miguel_page():
    # Real Miguel page is JS-rendered; use a static stub that mirrors the structure.
    html = (FIXTURES_DIR / "miguel_stub.html").read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")

@pytest.fixture
def friasneto_page():
    return _load_fixture("friasneto")
