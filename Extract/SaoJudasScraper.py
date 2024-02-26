import re

from config.ConfigManager import ConfigManager
from .BaseScraper import BaseScraper


class SaoJudasScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['SaoJudas']['url']
        self.set_breakpoint()
        self.step = config_manager['websites']['SaoJudas']['step']

    def set_breakpoint(self):
        content = self.get_page_content(f'{self.website_path}{0}')
        breakpoint = content.find('li', class_='paginate_button')
        x = breakpoint.find('a')['href']
        x = x.split('/')[-1]
        self.breakpoint = int(x)
        return 1

    def parse_page(self):
        for page in self.raw_websites:
            raw = page.find_all('p', class_='readmore text-right')
            for property_html in raw:
                info_list = self.get_page_content(property_html.find('a')['href']).find_all('ul')
                property_info = {
                    'preco': None,
                    'area': None,
                    'quartos': None,
                    'vagas': None,
                    'banheiros': None,
                    'bairro': 'Sem Bairro',
                    'tipo': 'Casa',
                    'Status': 'Compra',
                    'link': property_html.find('a')['href'],
                    'Imobiliaria': 'Sao_judas'
                }

                for info in info_list:
                    for i in info.find_all('p', class_='infos'):
                        text = i.text
                        value = i.find_next('span').text.strip()

                        if 'Quartos' in text:
                            property_info['quartos'] = value.replace(' ', '') if value else None
                            continue
                        elif 'Banheiros' in text:
                            property_info['banheiros'] = value.replace(' ', '') if value else None
                            continue
                        elif 'Garagens' in text:
                            property_info['vagas'] = value.replace(' ', '') if value else None
                            continue
                        elif 'Área' in text:
                            area = re.search(r"[\d.,]+", value)
                            property_info['area'] = area.group() if area else None
                            continue
                        elif 'Preço' in text:
                            price = re.search(r"[\d.,]+", value)
                            property_info['preco'] = float(
                                price.group().replace('.', '').replace(',', '.')) if price else None
                            continue
                        elif 'Bairro' in text:
                            property_info['bairro'] = value
                            continue

                self.raw_data.append(property_info)
        self.raw_websites = []
        return 1


