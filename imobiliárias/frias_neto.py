import requests
from bs4 import BeautifulSoup
import pandas as pd

# faz o request para a página https://www.friasneto.com.br/imoveis/todos-os-imoveis/comprar-ou-alugar/piracicaba/?locacao_venda=V
# e retorna o conteúdo da página
def get_page_content(request_url):
    # faz o request
    page_response = requests.get(request_url, timeout=5)
    # retorna o conteúdo da página em html
    return BeautifulSoup(page_response.content, "html.parser")


def extract_property_info(property_html):

    info_list = property_html.find_all("div", class_= "caption-line full")
    info_list = info_list[1].find_all('li')

    quartos = None
    vagas = None
    banheiros = None

    for info in info_list:
        if 'Quarto' in info.text:
            quartos = info.find('span').text.strip().replace('\n','').replace('Quartos', '').replace('Quarto', '').replace(' ', '').replace('2Quartos','2')
        elif 'Vaga' in info.text:
            vagas = info.find('span').text.strip().replace('Vagas', '').replace('Vaga', '').replace(' ', '')
        elif 'Banheiro' in info.text:
            banheiros = info.find('span').text.strip().replace('Banheiros', '').replace('Banheiro', '').replace(' ', '')


    price_element = property_html.find('p', class_='price')
    price = price_element.text.strip().replace(',','.').replace(' ', '').replace('Venda:R$', '') if 'Loca' not in price_element.text and 'Consulte' not in price_element.text else None
    price = price.replace('.', '') if price else None
    price = price[:-2] + '000' if price else None

    price = float(price) if price else None




    area_element = property_html.find('li').find('span')
    area = area_element.text.strip().replace(',','.').replace('M²', '').replace(' ', '') if area_element else None

    area = float(area) if area else None

    location_element = property_html.find('p', class_='neighborhood-city-titles')
    location = location_element.text.strip().replace(', Piracicaba', '') if location_element else None

    return {
        'preco': price,
        'area': area,
        'quartos': quartos,
        'vagas': vagas,
        'banheiros': banheiros,

        'bairro': location
    }


def run():
    full_property_info = []
    for i in range(300):
        old_page_content = None
        try:
            page_content = get_page_content(
                f'https://www.friasneto.com.br/imoveis/todos-os-imoveis/comprar-ou-alugar/piracicaba/?locacao_venda=V&id_cidade=2&pag={i}')

            if i > 1:
                old_page_content = get_page_content(
                f'https://www.friasneto.com.br/imoveis/todos-os-imoveis/comprar-ou-alugar/piracicaba/?locacao_venda=V&id_cidade=2&pag={i-1}')
        except:
            print('fim de scrape')
            break
        property_listings = page_content.find_all('div', class_='col-xs-12 col-sm-4 col-md-3 container-enterprises-item')
        if old_page_content:
            old_property_listings = old_page_content.find_all('div', class_='col-xs-12 col-sm-4 col-md-3 container-enterprises-item')
            if property_listings == old_property_listings:
                print('fim de scrape por repetição')
                break
        for property_listing in property_listings:
            property_info = extract_property_info(property_listing)
            full_property_info.append(property_info)


    df = pd.DataFrame(full_property_info)
    #dropa linhas com a coluna price vazia
    df = df.dropna(subset=['preco'])
    df = df.fillna(0)
    #converte a coluna price para float
    df['preco'] = df['preco'].astype(float)
    #converte a coluna area para float
    df['area'] = df['area'].astype(float)

    #converte valores de quartos, vagas e banheiros para int
    df['quartos'] = df['quartos'].astype(int)
    df['vagas'] = df['vagas'].astype(int)
    df['banheiros'] = df['banheiros'].astype(int)
    #trocar valores nulos por 0


    df['Imobiliaria'] = 'Frias Neto'
    df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
        #now, i write on a parquet file name imoveis
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a', header=False)
    return 1
