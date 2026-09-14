import re
import concurrent.futures

from config.ConfigManager import ConfigManager
from .BaseScraper import BaseScraper


class PremierScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        config_manager = ConfigManager().get_config()
        self.website_path = config_manager['websites']['Premier']['url']
        self.set_breakpoint()

    def set_breakpoint(self):
        content = self.get_page_content(f'{self.website_path}1/')
        pages = []
        if content:
            for a in content.find_all('a'):
                m = re.search(r'pagina-(\d+)', str(a))
                if m:
                    pages.append(int(m.group(1)))
        self.breakpoint = max(pages) if pages else 4
        return 1

    def fetch_page(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self.get_page_content, f'{self.website_path}{i}/'): i
                for i in range(1, self.breakpoint + 1)
            }
            for future in concurrent.futures.as_completed(future_to_url):
                if future.result():
                    self.raw_websites.append(future.result())

    def parse_page(self):
        tipos_validos = {
            'APARTAMENTO', 'CASA', 'TERRENO', 'SOBRADO',
            'KITNET', 'SALA', 'COBERTURA', 'CHÁCARA', 'CHACARA'
        }
        for page in self.raw_websites:
            for h3 in page.find_all('h3'):
                tipo_text = h3.text.strip().upper()
                if tipo_text not in tipos_validos:
                    continue

                h5 = h3.find_next('h5')
                price = None
                if h5:
                    price_text = (h5.text
                                  .replace('R$', '')
                                  .replace('.', '')
                                  .replace(',', '.')
                                  .strip())
                    try:
                        price = float(price_text)
                    except ValueError:
                        pass

                if not isinstance(price, float):
                    continue

                # Main link (comes after h5, wraps images + quartos/vagas/banheiros)
                main_link = h5.find_next('a', href=re.compile(r'/comprar/sp/piracicaba/'))
                if not main_link:
                    continue

                href = main_link.get('href', '')
                if '?favoritar' in href:
                    main_link = main_link.find_next('a', href=re.compile(r'/comprar/sp/piracicaba/(?!.*\?favoritar)'))
                    if not main_link:
                        continue
                    href = main_link.get('href', '')

                link = f'https://premierimoveispiracicaba.com.br{href}'

                parts = [p for p in href.split('/') if p]
                try:
                    idx = parts.index('piracicaba')
                    bairro = parts[idx + 1].replace('-', ' ').title()
                except (ValueError, IndexError):
                    bairro = 'Sem Bairro'

                text = main_link.get_text()
                q = re.search(r'(\d+)\s*quarto', text, re.IGNORECASE)
                b = re.search(r'(\d+)\s*banheiro', text, re.IGNORECASE)
                v = re.search(r'(\d+)\s*vaga', text, re.IGNORECASE)

                self.raw_data.append({
                    'preco': price,
                    'area': None,
                    'quartos': q.group(1) if q else None,
                    'vagas': v.group(1) if v else None,
                    'banheiros': b.group(1) if b else None,
                    'bairro': bairro,
                    'tipo': tipo_text.capitalize(),
                    'Status': 'Compra',
                    'link': link,
                    'Imobiliaria': 'Premier_imoveis'
                })

        self.raw_websites = []
        return 1
