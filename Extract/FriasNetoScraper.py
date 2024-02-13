from config.ConfigManager import ConfigManager
from bs4 import Tag
from .BaseScraper import BaseScraper


class FriasNetoScraper(BaseScraper):
    def __init__(self):
        super().__init__()

        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['FriasNeto']['url']
        self.set_breakpoint()

    def set_breakpoint(self):
        bp = self.get_page_content(f'{self.website_path}{0}')
        content = bp.find('ul', class_="pagination").find_all('a', {'data-page': True})
        self.breakpoint = int(content[-1].text.strip())
        return 1


    def parse_page(self):
        raw_property_info = [item for sublist in self.raw_websites for item in sublist if isinstance(item, Tag)]
        for page in raw_property_info:

            raw = page.find_all('div', class_='col-xs-12 col-sm-4 col-md-3 container-enterprises-item')
            for property_html in raw:
                info_list = property_html.find_all("div", class_="caption-line full")
                info_list = info_list[1].find_all('li')

                quartos = None
                vagas = None
                banheiros = None

                for info in info_list:
                    if 'Quarto' in info.text:
                        quartos = info.find('span').text.strip().replace('\n', '').replace('Quartos', '').replace('Quarto',
                                                                                                                  '').replace(
                            ' ', '').replace('2Quartos', '2')
                        continue
                    elif 'Vaga' in info.text:
                        vagas = info.find('span').text.strip().replace('Vagas', '').replace('Vaga', '').replace(' ', '')
                        continue
                    elif 'Banheiro' in info.text:
                        banheiros = info.find('span').text.strip().replace('Banheiros', '').replace('Banheiro', '').replace(
                            ' ', '')
                        continue

                price_element = property_html.find('p', class_='price')
                price = price_element.text.strip().replace(',', '.').replace(' ', '').replace('Venda:R$',
                                                                                              '') if 'Loca' not in price_element.text and 'Consulte' not in price_element.text and 'Quartos' not in price_element.text else None
                price = price.replace('.', '') if price else None
                price = price[:-2] + '000' if price else None
                tipo = property_html.find("div", class_="info_busca_imovel")
                tipo = 'Apartamento' if tipo else 'Casa'

                area_element = property_html.find('li').find('span')
                area = area_element.text.strip().replace(',', '.').replace('M²', '').replace(' ', '') if area_element and 'Quartos' not in area_element.text and 'Quarto' not in area_element.text else None
                try:
                    price = float(price) if price else None
                    area = float(area) if area else None
                except:
                    pass
                location_element = property_html.find('p', class_='neighborhood-city-titles')
                location = location_element.text.strip().replace(', Piracicaba', '') if location_element else None

                self.raw_data.append({
                    'preco': price/1000 if price else None,
                    'area': area,
                    'quartos': quartos,
                    'vagas': vagas,
                    'banheiros': banheiros,
                    'bairro': location,
                    'tipo': tipo,
                    'Status': 'Compra',
                    'link': 'https://www.friasneto.com.br' + property_html.find('a')['href'],
                    'Imobiliaria': 'Frias_neto'
                })
        self.raw_websites = []
        return 1
