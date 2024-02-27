from math import ceil

from config.ConfigManager import ConfigManager
from .BaseScraper import BaseScraper

class DuoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['Duo']['url']
        self.set_breakpoint()
        self.step = config_manager['websites']['Duo']['step']

    def set_breakpoint(self):
        content = self.get_page_content(f'{self.website_path}1')
        bp = content.find('span', class_='h-money')
        bp = bp.text.split('/')[0]
        self.breakpoint = ceil(int(bp.replace('.', '').strip()) / 12)
        return 1

    def parse_page(self):
        for page in self.raw_websites:
            raw = page.find_all('a', class_='card-with-buttons borderHover')
            for property_html in raw:
                quartos = None
                vagas = None
                banheiros = None
                area = None
                price = None
                location = 'Sem Bairro'
                info_list = property_html.find_all('li')
                for i in info_list:
                    if 'Quarto' in i.text:
                        quartos = i.text
                        quartos = quartos.replace('\n', '').replace('Quartos', '').replace('Quarto', '').replace(' ',
                                                                                                                 '').replace(
                            '2Quartos', '2') if quartos else None
                        continue
                    elif 'Banheiro' in i.text:
                        banheiros = i.text
                        banheiros = banheiros.replace('Banheiros', '').replace('Banheiro', '').replace(' ',
                                                                                                       '') if banheiros else None
                        continue
                    elif 'Vaga' in i.text:
                        vagas = i.text
                        vagas = vagas.replace('Vagas', '').replace('Vaga', '').replace(' ', '') if vagas else None
                        continue
                    elif 'm²' in i.text:
                        area = i.text
                        area = area.replace('m²', '').replace(' ', '') if area else None
                        continue

                location = property_html.find('h2', class_='card-with-buttons__heading')
                location = location.text.strip() if location else 'Sem Bairro'
                location = location.split('-')[0].strip()
                tipo = property_html.find('p', class_='card-with-buttons__title').text
                price = property_html.find('p', class_='card-with-buttons__value')
                try:
                    price = float(price.text.replace('R$', '')
                                  .replace('.', '')
                                  .replace(',', '.')
                                  .replace(' ', '')
                                  .replace('\n', '')
                                  .replace(',00', '')) if price else None
                except:
                    pass
                if isinstance(price, float):
                    self.raw_data.append({
                        'preco': price,
                        'area': area,
                        'quartos': quartos,
                        'vagas': vagas,
                        'banheiros': banheiros,
                        'bairro': location,
                        'tipo': tipo,
                        'Status': 'Compra',
                        'link': f"https://www.duoimoveis.com.br{property_html['href']}?from=sale",
                        'Imobiliaria':'Duo_imoveis'
                    })

        self.raw_websites = []
        return 1

