"""Bounded, sequential collection of publicly listed sale properties in SP."""
import re
import time
from urllib.parse import urljoin, urlparse
from .BaseScraper import BaseScraper
from config.ConfigManager import ConfigManager


def number(value):
    return float(value.replace(".", "").replace(",", "."))


class SaoPauloScraper(BaseScraper):
    source = "LopesLT"

    def __init__(self):
        super().__init__()
        self.settings = ConfigManager().get_config()["websites"][self.source]
        self.website_path = self.settings["url"]

    def scrape(self):
        for page in range(1, self.settings.get("max_pages", 2) + 1):
            url = self.website_path if page == 1 else f"{self.website_path}?page={page}"
            soup = self.get_page_content(url)
            if soup is None:
                raise RuntimeError(f"Não foi possível acessar {self.website_path}")
            self.raw_websites = [soup]
            previous = len(self.raw_data)
            self.parse_page()
            if len(self.raw_data) == previous:
                break
            self.raw_data = list({p["link"]: p for p in self.raw_data}.values())
            if len(self.raw_data) == previous:
                break
            time.sleep(1)
        if not self.raw_data:
            raise RuntimeError(f"Nenhum anúncio de venda de São Paulo encontrado em {self.source}")
        return self.raw_data

    def parse_page(self):
        for soup in self.raw_websites:
            for card in soup.select("article.vp-property-card"):
                title = card.select_one("h3 a[href]")
                if not title or "venda" not in title.get_text().lower():
                    continue
                content = card.get_text(" ", strip=True)
                location = re.search(r"([^,]+), São Paulo - SP", content)
                price = re.search(r"R\$\s*([\d.,]+)", content)
                area = re.search(r"([\d.,]+)\s*m\s*[²2]", content)
                if not location or not price or not area:
                    continue
                # Location is a dedicated span; avoid photo counts/SKU in text.
                location_span = next((s for s in card.select("span") if re.fullmatch(r".+, São Paulo - SP", s.get_text(strip=True))), None)
                if location_span is None:
                    continue
                def count(pattern):
                    match = re.search(pattern, content)
                    return int(match.group(1)) if match else None
                link = urljoin(self.website_path, title["href"])
                if urlparse(link).netloc != urlparse(self.website_path).netloc:
                    continue
                self.raw_data.append({"preco": number(price.group(1)), "area": float(area.group(1).replace(",", ".")),
                    "quartos": count(r"(\d+) quartos?"), "banheiros": count(r"(\d+) banheiros?"), "vagas": count(r"(\d+) vagas?"),
                    "bairro": location_span.get_text(strip=True).split(",")[0], "cidade": "São Paulo", "uf": "SP",
                    "tipo": title.get_text(strip=True).split()[0], "Status": "Compra", "link": link, "Imobiliaria": self.source})
        self.raw_websites = []


class LopesLTScraper(SaoPauloScraper):
    source = "LopesLT"
