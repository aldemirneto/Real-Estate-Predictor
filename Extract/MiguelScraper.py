import re
import concurrent.futures
from math import ceil

from config.ConfigManager import ConfigManager
from .BaseScraper import BaseScraper


class MiguelScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['Miguel']['url']
        self.set_breakpoint()

    def set_breakpoint(self):
        # Miguel's full catalogue requires JS pagination; static fetch returns the
        # first batch of results directly from /venda/residencial/.
        self.breakpoint = 1
        return 1

    def fetch_page(self):
        page = self.get_page_content(self.website_path)
        if page:
            self.raw_websites.append(page)

    def parse_page(self):
        for page in self.raw_websites:
            cards = page.find_all('a', href=re.compile(r'miguelimoveis\.com\.br/imovel/'))
            for card in cards:
                try:
                    link = card.get('href', '')

                    price = None
                    for div in card.find_all('div'):
                        if 'Venda R$' in div.text and 'Aluguel' not in div.text:
                            price_text = (div.text
                                          .replace('Venda R$', '')
                                          .replace('\n', '')
                                          .replace('.', '')
                                          .replace(',', '.')
                                          .strip())
                            try:
                                price = float(price_text)
                            except ValueError:
                                pass
                            break

                    if not isinstance(price, float):
                        continue

                    h4 = card.find('h4')
                    bairro = h4.text.split(' - ')[0].strip() if h4 else 'Sem Bairro'

                    h3 = card.find('h3')
                    tipo = h3.text.split()[0] if h3 else 'Indefinido'

                    quartos = vagas = area = None
                    for span in card.find_all('span'):
                        t = span.text.strip()
                        if 'Quarto' in t:
                            quartos = re.sub(r'[^\d]', '', t.replace('Quartos', '').replace('Quarto', '')) or None
                        elif 'Vaga' in t:
                            vagas = re.sub(r'[^\d]', '', t.replace('Vagas', '').replace('Vaga', '')) or None
                        elif 'm²' in t:
                            m = re.search(r'([\d]+)', t)
                            if m:
                                try:
                                    area = float(m.group(1))
                                except ValueError:
                                    pass

                    self.raw_data.append({
                        'preco': price,
                        'area': area,
                        'quartos': quartos,
                        'vagas': vagas,
                        'banheiros': None,
                        'bairro': bairro,
                        'tipo': tipo,
                        'Status': 'Compra',
                        'link': link,
                        'Imobiliaria': 'Miguel_imoveis'
                    })
                except Exception:
                    continue

        self.raw_websites = []
        return 1
