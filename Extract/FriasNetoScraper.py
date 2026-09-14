import re

from config.ConfigManager import ConfigManager
from .BaseScraper import BaseScraper

BASE_URL = "https://www.friasneto.com.br"


class FriasNetoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['FriasNeto']['url']
        self.set_breakpoint()

    def set_breakpoint(self):
        content = self.get_page_content(self.website_path)
        self.breakpoint = 1
        if content:
            pages = []
            for a in content.find_all('a', href=True):
                m = re.search(r'pag=(\d+)', a['href'])
                if m:
                    pages.append(int(m.group(1)))
            if pages:
                self.breakpoint = max(pages)
        return 1

    def fetch_page(self):
        urls = [f"{self.website_path}?pag={n}" for n in range(1, self.breakpoint + 1)]
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as ex:
            pages = list(ex.map(self.get_page_content, urls))
        self.raw_websites = [p for p in pages if p]

    def parse_page(self):
        for page in self.raw_websites:
            for card in page.find_all('div', class_='card-imo'):
                try:
                    a_tag = card.find('a', href=True)
                    href = a_tag['href'] if a_tag else None
                    if not href:
                        continue
                    link = href if href.startswith('http') else f"{BASE_URL}/{href.lstrip('/')}"

                    price = None
                    valores = card.find('div', class_='card-valores')
                    if valores:
                        m = re.search(r'R\$\s*([\d.,]+)', valores.text)
                        if m:
                            try:
                                price = float(m.group(1).replace('.', '').replace(',', '.'))
                            except ValueError:
                                pass

                    loc_tag = card.find('div', class_='card-bairro-cidade-texto')
                    bairro = loc_tag.text.split(' - ')[0].strip() if loc_tag else 'Sem Bairro'

                    titulo = card.find('h2', class_='card-titulo')
                    tipo = titulo.text.strip().split()[0] if titulo else 'Indefinido'

                    def _num(cls):
                        tag = card.find('div', class_=cls)
                        if not tag:
                            return None
                        m = re.search(r'\d+', tag.text)
                        return m.group() if m else None

                    self.raw_data.append({
                        'preco':      price,
                        'area':       None,
                        'quartos':    _num('dorm-ico'),
                        'vagas':      _num('gar-ico'),
                        'banheiros':  _num('banh-ico'),
                        'bairro':     bairro,
                        'tipo':       tipo,
                        'Status':     'Compra',
                        'link':       link,
                        'Imobiliaria': 'Frias_neto',
                    })
                except Exception:
                    continue

        self.raw_websites = []
        return 1
