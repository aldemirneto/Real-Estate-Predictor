import concurrent.futures
import time
from math import ceil

import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_page_content(request_url):
    # faz o request
    page_response = requests.get(request_url, timeout=10, allow_redirects=False, headers={"User-Agent": "Mozilla/5.0"})
    # retorna o conteúdo da página em html
    return BeautifulSoup(page_response.content, "html.parser")


def extract_property_info(property_html):
    try:
        info_list = property_html.find("div", class_="theInfos").find('ul', class_='attr').find_all('li')
    except:
        print('página zoada')
        return {
            'preco': 0,
            'area': 0,
            'quartos': 0,
            'vagas': 0,
            'banheiros': 0,
            'bairro': 'Sem Bairro',
            'link': 'Sem link'
        }

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
                .replace(',', '.') \
                .replace('.', '')
            area = float(area) if area else None
            continue

    price_element = property_html.find('span', class_='price')
    price = price_element.text.strip().replace('Aluguel:R$ ',
                                               '') if price_element and 'consultar' not in price_element.text else None
    price = price.replace(',', '.').replace('.', '') if price else None

    location_element = property_html.find_all('span', class_='extra')
    location_element = location_element[1]
    location = location_element.text.strip() \
        .replace('Bairro: ', '') if location_element else None
    link = property_html.find("div", class_="theInfos").find('a')['href']

    return {
        'preco': price,
        'area': area,
        'quartos': quartos,
        'vagas': vagas,
        'banheiros': banheiros,
        'bairro': location,
        'link': link
    }


def set_breakpoint(url: str):
    content = get_page_content(url)
    bp = content.find('div', class_='total').text
    # replace untill the first letter is found
    first_non_digit_index = next((i for i, char in enumerate(bp) if not char.isdigit()), None)
    bp = bp[:first_non_digit_index]
    return ceil(int(bp) / 12)


def run():
    full_property_info = []
    raw_property_info = []
    break_point = set_breakpoint(f'https://www.imobiliariajunqueira.com.br/alugar/todas?page=0')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(get_page_content, f'https://www.imobiliariajunqueira.com.br/alugar/todas?page={i}'): i for
            i in range(break_point)}
        for future in concurrent.futures.as_completed(future_to_url):
            raw_property_info.append(future.result().find_all('div', class_='item-wrap'))

    raw_property_info = [item for sublist in raw_property_info for item in sublist]
    full_property_info = [extract_property_info(property_html) for property_html in raw_property_info]
    # now i do a dataframe with the full_property_info, and a column with the name 'Junqueira' and the date of today
    df = pd.DataFrame(full_property_info)
    # dropa linhas com a coluna price vazia
    df = df.dropna(subset=['preco'])
    df = df.fillna(0)
    try:
        # converte a coluna price para float
        df['preco'] = df['preco'].astype(float)
        df['preco'] = df['preco'] / 100
        # converte a coluna area para float
        df['area'] = df['area'].astype(float)
        # divido a area por 1000 e arredondo uma casa para todos os valores da coluna area
        df['area'] = round(df['area'] / 100, 1)
        # converte valores de quartos, vagas e banheiros para int
        df['quartos'] = df['quartos'].astype(int)
        df['vagas'] = df['vagas'].astype(int)
        df['banheiros'] = df['banheiros'].astype(int)
    except:
        print('erro na conversão de tipos junqueira')
        pass
    df['Imobiliaria'] = 'Junqueira'
    df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df['last_seen'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df = df[
        ['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro', 'Data_scrape', 'last_seen']]
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a', header=False)
    return 1



run()