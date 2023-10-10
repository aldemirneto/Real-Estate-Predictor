import concurrent.futures
import time
from math import ceil

import requests
from bs4 import BeautifulSoup
import pandas as pd
def get_page_content(request_url):
    # faz o request
    page_response = requests.get(request_url, timeout=10, allow_redirects=False, headers={"User-Agent":"Mozilla/5.0"})
    # retorna o conteúdo da página em html
    return BeautifulSoup(page_response.content, "html.parser")


def extract_property_info(property_html, link):
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
            quartos = quartos.replace('\n','').replace('Quartos', '').replace('Quarto', '').replace(' ', '').replace('2Quartos','2') if quartos else None
            continue
        elif 'Banheiro' in i.text:
            banheiros = i.text
            banheiros = banheiros.replace('Banheiros', '').replace('Banheiro', '').replace(' ', '') if banheiros else None
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
    price = property_html.find('p', class_ = 'card-with-buttons__value').text
    try:
        price = float(price.replace('R$', '')
                        .replace('.', '')
                        .replace(',', '.')
                        .replace(' ', '')
                        .replace('\n', '')
                        .replace(',00','')) if price else None
    except:
        pass
    return{
            'preco': price,
            'area': area,
            'quartos': quartos,
            'vagas': vagas,
            'banheiros': banheiros,
            'bairro': location,
            'link': link
        }




def set_breakpoint(url: str):
    content = get_page_content(f'{url}1')
    bp = content.find('span', class_='h-money')
    #slice the content untill the first '\'
    bp = bp.text.split('/')[0]


    return ceil(int(bp.replace('.','').strip())/12)



def run():
    urls = ['https://www.duoimoveis.com.br/imoveis/a-venda/piracicaba?pagina=']
    full_property_info = []
    raw_property_info = []
    for url in urls:
        break_point = set_breakpoint(url)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {
                executor.submit(get_page_content, f'https://www.duoimoveis.com.br/imoveis/a-venda/piracicaba?pagina={i}'): i
                for
                i in range(break_point+1)}
            for future in concurrent.futures.as_completed(future_to_url):
                raw_property_info.append(
                    future.result().find_all('a', class_='card-with-buttons borderHover'))

    raw_property_info = [item for sublist in raw_property_info for item in sublist]
    full_property_info = [extract_property_info(property_html=property_html, link=f"https://www.duoimoveis.com.br{property_html['href']}?from=sale") for property_html in raw_property_info]
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
    df['Imobiliaria'] = 'duo imoveis'
    df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df['last_seen'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df = df[['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro', 'Data_scrape', 'last_seen']]
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a',  header=False)
    return 1


