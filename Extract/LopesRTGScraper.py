import json
import re
import time
from urllib.parse import urljoin, urlparse
from .SaoPauloScraper import SaoPauloScraper


class LopesRTGScraper(SaoPauloScraper):
    source = "LopesRTG"

    def scrape(self):
        page = self.get_page_content(self.website_path)
        if page is None:
            raise RuntimeError("Não foi possível acessar Lopes RTG")
        links = list(dict.fromkeys(urljoin(self.website_path, a["href"]) for a in page.select('a[href*="/imovel/"]')))
        for link in links[:self.settings.get("max_properties", 10)]:
            if urlparse(link).netloc != urlparse(self.website_path).netloc:
                continue
            detail = self.get_page_content(link)
            if detail is not None:
                self.parse_detail(detail, link)
            time.sleep(1)
        if not self.raw_data:
            raise RuntimeError("Nenhum anúncio válido na Lopes RTG")
        return self.raw_data

    def parse_detail(self, page, link):
        for script in page.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or script.get_text())
            except (ValueError, TypeError):
                continue
            for item in data.get("@graph", [data]) if isinstance(data, dict) else data:
                offer = item.get("offers", {})
                address = item.get("address", {})
                if not isinstance(offer, dict) or not offer.get("businessFunction", "").endswith("#Sell"):
                    continue
                city = address.get("addressLocality", "")
                # Some source JSON strings contain double escaped unicode.
                if "\\u" in city:
                    city = city.encode().decode("unicode_escape")
                if city != "São Paulo":
                    continue
                text = page.get_text(" ", strip=True).split("Imóveis similares")[0]
                location = re.search(r"Localização: [^,]+, ([^,]+), São Paulo", text)
                parking = re.search(r"Vagas de garagem: (\d+)", text)
                if not location:
                    continue
                self.raw_data.append({"preco": float(offer["price"]), "area": float(item["floorSize"]["value"]),
                    "quartos": int(item.get("numberOfBedrooms", 0)), "banheiros": int(item.get("numberOfBathroomsTotal", 0)),
                    "vagas": int(parking.group(1)) if parking else None, "bairro": location.group(1),
                    "cidade": "São Paulo", "uf": "SP", "tipo": "Apartamento", "Status": "Compra", "link": link, "Imobiliaria": self.source})
