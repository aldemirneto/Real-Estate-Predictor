"""Parse public SP Imóvel agency cards; no contact forms or authenticated data."""
import math
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_URL = 'https://www.spimovel.com.br'
DIRECTORY_URL = BASE_URL + '/imobiliarias/sao-paulo/sp/'
DIRECTORY_API = BASE_URL + '/Imobiliaria/JsGetImobiliariaPaginacao'


def parse_directory_page(rows):
    return [{
        'id': int(r['ImobiliariaId']), 'nome': r['Imobiliaria'], 'bairro': r.get('Bairro'),
        'cidade': r.get('Cidade'), 'creci': r.get('Creci'),
        'url': urljoin(BASE_URL, r['Url']),
        'tipo_registro': 'empresa' if (r.get('Creci') or '').strip().endswith('J') else 'corretor',
    } for r in rows if r.get('ImobiliariaId') and r.get('Cidade') == 'São Paulo'
        and urlparse(urljoin(BASE_URL, r.get('Url', ''))).netloc == urlparse(BASE_URL).netloc]


def parse_directory_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    agencies = {}
    for a in soup.select('a[href^="/imobiliaria/"]'):
        paragraphs = a.select('p')
        creci = a.select_one('.creci')
        match = re.search(r'/(\d+)/?$', a['href'])
        if len(paragraphs) < 2 or not creci or not match:
            continue
        location = paragraphs[1].get_text(' ', strip=True)
        if not location.endswith(', São Paulo'):
            continue
        registration = creci.get_text(' ', strip=True).replace('CRECI:', '').strip()
        agency_id = int(match.group(1))
        agencies[agency_id] = {'id': agency_id, 'nome': paragraphs[0].get_text(' ', strip=True),
            'bairro': location.rsplit(',', 1)[0].strip(), 'cidade': 'São Paulo', 'creci': registration,
            'url': urljoin(BASE_URL, a['href']), 'tipo_registro': 'empresa' if registration.endswith('J') else 'corretor'}
    return list(agencies.values())


def parse_agency_page(html, agency):
    soup = BeautifulSoup(html, 'html.parser')
    count = soup.select_one('input[name="txtCount"]')
    size = soup.select_one('input[name="txtItens"]')
    if count is None or size is None:
        raise ValueError('Página sem contagem de catálogo reconhecida')
    expected = int(count.get('value', 0))
    per_page = int(size.get('value', 15)) or 15
    title = soup.select_one('.imobiliaria h1')
    if title is None:
        raise ValueError('Página de imobiliária não reconhecida')
    agency_input = soup.select_one('input#ImobiliariaId')
    if agency_input is None or agency_input.get('value') != str(agency['id']):
        raise ValueError('Catálogo não corresponde à imobiliária solicitada')
    records, all_ids = [], []
    for card in soup.select('.lista-anuncio .anuncio'):
        link = card.select_one('h2.h2-tipo a[href]')
        operation = card.select_one('[data-finalidadeid]')
        if not link:
            continue
        all_ids.append(link.get('data-imovelid') or link['href'])
        if operation is None or operation.get('data-finalidadeid') != '1':
            continue
        location = card.select_one('h3.h2-regiao.titulo')
        price = card.select_one('h3.valor')
        if location is None or price is None:
            continue
        parts = re.split(r'\s+-\s+', location.get_text(' ', strip=True))
        if len(parts) < 2 or parts[-1] != 'São Paulo':
            continue
        price_match = re.search(r'R\$\s*([\d.,]+)', price.get_text(' ', strip=True))
        if not price_match:
            continue
        value = float(price_match.group(1).replace('.', '').replace(',', '.'))
        if not math.isfinite(value) or value <= 0:
            continue
        def feature(selector):
            icon = card.select_one(selector)
            return icon.parent.get_text(' ', strip=True) if icon else ''
        def integer(selector):
            match = re.search(r'\d+', feature(selector))
            return int(match.group()) if match else None
        area_text = feature('.especificacoes-mobile .ico-area')
        area_match = re.search(r'([\d.,]+)\s*m', area_text)
        area = float(area_match.group(1).replace('.', '').replace(',', '.')) if area_match else None
        # Area format uses Brazilian separators in this portal.
        link_url = urljoin(BASE_URL, link['href'])
        if urlparse(link_url).netloc != urlparse(BASE_URL).netloc:
            continue
        records.append({
            'preco': value, 'area': area, 'quartos': integer('.especificacoes-mobile .ico-quartos'),
            'vagas': integer('.especificacoes-mobile .ico-vagas'), 'banheiros': None,
            'bairro': ' - '.join(parts[:-1]), 'cidade': 'São Paulo', 'uf': 'SP',
            'tipo': re.split(r' para | à venda', link.get_text(' ', strip=True), maxsplit=1)[0],
            'link': link_url, 'imobiliaria': agency['nome'], 'status': 'Compra',
            'source_portal': 'SPImovel', 'agency_id': agency['id'],
        })
    return records, max(1, math.ceil(expected / per_page)), tuple(all_ids), expected
