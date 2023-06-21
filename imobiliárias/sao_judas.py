import concurrent.futures
import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
def get_page_content(request_url):
    # faz o request
    page_response = requests.get(request_url, timeout=5)
    # retorna o conteúdo da página em html
    return BeautifulSoup(page_response.content, "html.parser")


import re

def extract_property_info(link):

    info_list = get_page_content(link).find_all('ul')
    property_info = {
        'preco': None,
        'area': None,
        'quartos': None,
        'vagas': None,
        'banheiros': None,
        'bairro': 'Sem Bairro',
        'link': link
    }

    for info in info_list:
        for i in info.find_all('p', class_='infos'):
            text = i.text
            value = i.find_next('span').text.strip()

            if 'Quartos' in text:
                property_info['quartos'] = value.replace(' ', '') if value else None
            elif 'Banheiros' in text:
                property_info['banheiros'] = value.replace(' ', '') if value else None
            elif 'Garagens' in text:
                property_info['vagas'] = value.replace(' ', '') if value else None
            elif 'Área' in text:
                area = re.search(r"[\d.,]+", value)
                property_info['area'] = area.group() if area else None
            elif 'Preço' in text:
                price = re.search(r"[\d.,]+", value)
                property_info['preco'] = float(price.group().replace('.', '').replace(',', '.')) if price else None
            elif 'Bairro' in text:
                property_info['bairro'] = value

    return property_info




def set_breakpoint(url: str):
    content = get_page_content(url)
    breakpoint = content.find('li', class_='paginate_button')
    x = breakpoint.find('a')['href']
    x = x.split('/')[-1]
    return int(x)





def run():
    urls = ['https://www.imobiliariasjudas.com.br/venda-de-casa/', 'https://www.imobiliariasjudas.com.br/venda-de-apartamento/', 'https://www.imobiliariasjudas.com.br/venda-de-imovel-comercial/']
    full_property_info = []
    raw_property_info = []
    for url in urls:
        break_point = set_breakpoint(url)

        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(get_page_content, f'{url}{i}'): i for i in range(0,break_point,20)}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    raw_property_info.append(future.result().find_all('p', class_='readmore text-right'))
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))

    raw_property_info = [item for sublist in raw_property_info for item in sublist]
    full_property_info = [extract_property_info(property.find('a')['href']) for property in raw_property_info]
    df = pd.DataFrame(full_property_info)
    #dropa linhas com a coluna price vazia
    df = df.dropna(subset=['preco'])
    df = df.fillna(0)
    try:
        #converte a coluna price para float
        df['preco'] = df['preco'].astype(float)
        #converte a coluna area para float
        df['area'] = df['area'].astype(float)
        #converte valores de quartos, vagas e banheiros para int
        df['quartos'] = df['quartos'].astype(int)
        df['vagas'] = df['vagas'].astype(int)
        df['banheiros'] = df['banheiros'].astype(int)
    except:
        pass
    df['Imobiliaria'] = 'Sâo Judas'
    df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df['last_seen'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df = df[['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro', 'Data_scrape', 'last_seen']]
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a',  header=False)
    return 1

