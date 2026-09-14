import re
from math import ceil

from bs4 import Tag

from config.ConfigManager import ConfigManager
from .BaseScraper import BaseScraper


class JunqueiraScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['Junqueira']['url']
        self.set_breakpoint()

    def set_breakpoint(self):
        content = self.get_page_content(f'{self.website_path}{0}')
        bp = content.find('div', class_='desktop-navigation').text
        bp = [n for n in bp.split(' ') if n.isdigit()][-1]
        self.breakpoint = ceil(int(bp) / 12)
        return 1


    def parse_page(self):
        raw_property_info = [item for sublist in self.raw_websites for item in sublist if isinstance(item, Tag)]
        for page in raw_property_info:
            raw = page.find_all('div', class_='item-wrap')
            for property_html in raw:
                try:
                    info_list = property_html.find("div", class_="theInfos").find('ul', class_='attr').find_all('li')
                except Exception:
                    continue

                quartos = None
                vagas = None
                banheiros = None
                area = None

                for info in info_list:
                    if 'quarto' in info.text:
                        quartos = info.text.strip().replace('\n', '') \
                            .replace(' ', '') \
                            .replace('suítes', '') \
                            .replace('quartos', '') \
                            .replace('quarto', '') \
                            .replace('suíte', '')
                        continue

                    elif 'vaga' in info.text:
                        vagas = info.text.strip().replace('\n', '') \
                            .replace(' ', '') \
                            .replace('vagas', '') \
                            .replace('vaga', '')
                        continue
                    elif 'suíte' in info.text:
                        if quartos is None:
                            quartos = info.text.strip().replace('\n', '') \
                                .replace(' ', '') \
                                .replace('suítes', '') \
                                .replace('suíte', '')
                        banheiros = info.text.strip().replace('\n', '') \
                            .replace(' ', '') \
                            .replace('suítes', '') \
                            .replace('suíte', '')
                        continue
                    elif 'm²' in info.text:
                        area = info.text.strip().replace('\n', '') \
                            .replace(' ', '') \
                            .replace('m²', '') \
                            .replace(',', '.')
                        try:
                            area = float(area) if area else None
                        except (ValueError, TypeError):
                            area = None
                        continue

                price_element = property_html.find('span', class_='price')
                price = None
                if price_element and 'consultar' not in price_element.text.lower():
                    m = re.search(r'[\d.,]+', price_element.text.replace('\n', '').replace(' ', ''))
                    if m:
                        price = m.group().replace('.', '').replace(',', '')

                location_element = property_html.find_all('span', class_='extra')
                tipo = location_element[0].text.split(' ')[0]
                location_element = location_element[1]
                location = location_element.text.strip() \
                    .replace('Bairro: ', '') if location_element else None
                link = property_html.find("div", class_="theInfos").find('a')['href']

                self.raw_data.append({
                    'preco': float(price)/100 if price else 0,
                    'area': area,
                    'quartos': quartos,
                    'vagas': vagas,
                    'banheiros': banheiros,
                    'bairro': location,
                    'tipo': tipo,
                    'Status': 'Compra',
                    'link': link,
                    'Imobiliaria': 'Junqueira'
                })
        self.raw_websites = []
        return 1
