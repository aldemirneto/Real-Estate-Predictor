import concurrent.futures
import time

import requests
from bs4 import BeautifulSoup
import pandas as pd

# faz o request para a página https://www.friasneto.com.br/imoveis/todos-os-imoveis/comprar-ou-alugar/piracicaba/?locacao_venda=V
# e retorna o conteúdo da página
def get_page_content(request_url):
    # faz o request
    page_response = requests.get(request_url, timeout=10, allow_redirects=False, headers={"User-Agent": "Mozilla/5.0"})
    # retorna o conteúdo da página em html
    return BeautifulSoup(page_response.content, "html.parser")


def set_breakpoint(url:str):
    bp = get_page_content(url)
    content = bp.find('ul',class_="pagination" ).find_all('a', {'data-page': True})
    return int(content[-1].text.strip())




def extract_property_info(property_html):

    info_list = property_html.find_all("div", class_= "caption-line full")
    info_list = info_list[1].find_all('li')

    quartos = None
    vagas = None
    banheiros = None

    for info in info_list:
        if 'Quarto' in info.text:
            quartos = info.find('span').text.strip().replace('\n','').replace('Quartos', '').replace('Quarto', '').replace(' ', '').replace('2Quartos','2')
            continue
        elif 'Vaga' in info.text:
            vagas = info.find('span').text.strip().replace('Vagas', '').replace('Vaga', '').replace(' ', '')
            continue
        elif 'Banheiro' in info.text:
            banheiros = info.find('span').text.strip().replace('Banheiros', '').replace('Banheiro', '').replace(' ', '')
            continue


    price_element = property_html.find('p', class_='price')
    price = price_element.text.strip().replace(',','.').replace(' ', '').replace('Venda:R$', '') if 'Loca' not in price_element.text and 'Consulte' not in price_element.text and 'Quartos' not in price_element.text else None
    price = price.replace('.', '') if price else None
    price = price[:-2] + '000' if price else None

    area_element = property_html.find('li').find('span')
    area = area_element.text.strip().replace(',','.').replace('M²', '').replace(' ', '') if area_element  and 'Quartos' not in area_element.text else None
    try:
        price = float(price) if price else None
        area = float(area) if area else None
    except:
        pass
    location_element = property_html.find('p', class_='neighborhood-city-titles')
    location = location_element.text.strip().replace(', Piracicaba', '') if location_element else None

    return {
        'preco': price,
        'area': area,
        'quartos': quartos,
        'vagas': vagas,
        'banheiros': banheiros,

        'bairro': location,
        'link': 'https://www.friasneto.com.br'+property_html.find('a')['href']
    }


def run():

    raw_property_info = []
    breakpoint = set_breakpoint(f'https://www.friasneto.com.br/imoveis/todos-os-imoveis/comprar-ou-alugar/piracicaba/?locacao_venda=V&id_cidade=2&pag=0)')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(get_page_content, f'https://www.friasneto.com.br/imoveis/todos-os-imoveis/comprar-ou-alugar/piracicaba/?locacao_venda=V&id_cidade=2&pag={i}'): i for
            i in range(breakpoint)}
        for future in concurrent.futures.as_completed(future_to_url):
            raw_property_info.append(future.result().find_all('div', class_='col-xs-12 col-sm-4 col-md-3 container-enterprises-item'))

    raw_property_info = [item for sublist in raw_property_info for item in sublist]
    full_property_info = [extract_property_info(property_html) for property_html in raw_property_info]
    df = pd.DataFrame(full_property_info)
    #dropa linhas com a coluna price vazia
    df = df.dropna(subset=['preco'])
    df = df.fillna(0)
    #converte a coluna price para float
    try:
        df['preco'] = df['preco'].astype(float)
        df['preco'] = df['preco']/1000
        #converte a coluna area para float
        df['area'] = df['area'].astype(float)

        #converte valores de quartos, vagas e banheiros para int
        df['quartos'] = df['quartos'].astype(int)
        df['vagas'] = df['vagas'].astype(int)
        df['banheiros'] = df['banheiros'].astype(int)

    except Exception as e:
        print('erro na conversão de tipos')
        pass

    df['Imobiliaria'] = 'Frias Neto'
    df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df['last_seen'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df = df[['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro', 'Data_scrape', 'last_seen']]
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a', header=False)
    return 1
