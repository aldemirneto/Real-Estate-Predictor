from config.ConfigManager import ConfigManager
from .BaseScraper import BaseScraper

class AtoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['Ato']['url']
        self.set_breakpoint()

    def set_breakpoint(self):
        self.breakpoint = 255
        return 1

    def parse_page(self):
        for page in self.raw_websites:
            raw = page.find_all('div', class_='imagenet-pesquisa-imovel')
            for div_imovel in raw:
                try:
                    preco = div_imovel.select_one('.imagenet-pesquisa-imovel-valor').text
                    preco = preco.replace('R$ ', '').replace(',', '.').strip()
                    preco = float(preco)
                except:
                    preco = None
                try:
                    area = div_imovel.select_one('.imagenet-pesquisa-imovel-area').text
                    area = area.replace('m²', '').strip()
                    area = float(area)
                except:
                    area = None
                try:
                    quartos = div_imovel.select_one('.imagenet-pesquisa-imovel-dormitorios').text.strip()
                    quartos = quartos.replace('N/a', '0')
                    quartos = int(quartos)
                except:
                    quartos = 0
                try:
                    vagas = div_imovel.select_one('.imagenet-pesquisa-imovel-garagem').text.strip()
                    vagas = vagas.replace('N/a', '0').strip()
                    vagas = int(vagas)
                except:
                    vagas = 0
                try:
                    banheiros = div_imovel.select_one('.imagenet-pesquisa-imovel-banheiros').text.strip()
                except:
                    banheiros = 0
                try:
                    bairro = div_imovel.select_one('.imagenet-pesquisa-imovel-titulo').text.strip()
                    bairro = bairro.split(',')[0].strip()
                    bairro = bairro.replace(' ', '_')

                except:
                    bairro = None
                try:
                    link = div_imovel.select_one('a')['href']
                except:
                    link = None
                try:
                    tipo = div_imovel.select_one('.imagenet-pesquisa-imovel-tipo').text.strip()
                    tipo = tipo.replace('Á', 'A')
                except:
                    tipo = None


                imovel_info = {
                    'preco': preco,
                    'area': area,
                    'quartos': quartos,
                    'vagas': vagas,
                    'banheiros': banheiros,
                    'bairro': bairro,
                    'tipo': tipo,
                    'Status': 'Compra',
                    'link': link,
                    'Imobiliaria': 'Ato'
                }

                self.raw_data.append(imovel_info)
        self.raw_websites = []
        return 1



