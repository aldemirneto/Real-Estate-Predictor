import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_page_content(request_url):
    # faz o request
    page_response = requests.get(request_url, timeout=5)
    # retorna o conteúdo da página em html
    return BeautifulSoup(page_response.content, "html.parser")


def extract_property_info(property_html):
    try:
        info_list = property_html.find("div", class_= "theInfos").find('ul', class_='attr').find_all('li')
    except:
        print('página zoada')
        return {
        'preco':0,
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
    area= None

    for info in info_list:
        if 'quarto' in info.text:
            quartos = info.text.strip().replace('\n','')\
                                        .replace(' ', '')\
                                        .replace('suítes','')\
                                        .replace('quartos', '')\
                                        .replace('quarto', '') \
                                        .replace('suíte', '')
                                        

        elif 'vaga' in info.text:
            vagas = info.text.strip().replace('\n','')\
                                     .replace(' ', '')\
                                     .replace('vagas', '')\
                                     .replace('vaga', '')
        elif 'suíte' in info.text:
            if quartos is None:
                quartos = info.text.strip().replace('\n','')\
                                            .replace(' ', '')\
                                            .replace('suítes','') \
                                            .replace('suíte', '')
            banheiros = info.text.strip().replace('\n','')\
                                        .replace(' ', '')\
                                        .replace('suítes','')\
                                        .replace('suíte', '')
        elif 'm²' in info.text:
            area = info.text.strip().replace('\n','')\
                                    .replace(' ', '')\
                                    .replace('m²','')\
                                    .replace(',', '.')\
                                    .replace('.', '')
            area = float(area) if area else None


    price_element = property_html.find('span', class_='price')
    price = price_element.text.strip().replace('Venda:R$ ', '') if price_element and 'consultar' not in price_element.text else None
    price = price.replace(',', '.').replace('.', '') if price else None


    location_element = property_html.find_all('span', class_='extra')
    location_element = location_element[1]
    location = location_element.text.strip()\
                                     .replace('Bairro: ', '')if location_element else None
    link = property_html.find("div", class_= "theInfos").find('a')['href']

    return {
        'preco': price,
        'area': area,
        'quartos': quartos,
        'vagas': vagas,
        'banheiros': banheiros,
        'bairro': location,
        'link': link
    }


def run():
    full_property_info = []

    for i in range(300):
        page_content = None
        old_page_content = None
        try:
            page_content = get_page_content(
                f'https://www.imobiliariajunqueira.com.br/comprar/todas?page={i}')
            if i > 1:
                old_page_content = get_page_content(f'https://www.imobiliariajunqueira.com.br/comprar/todas?page={i-1}')

        except:
            print('pagina zoada')
            continue


        property_listings = page_content.find_all('div', class_='item-wrap')
        if old_page_content:
            old_property_listings = old_page_content.find_all('div', class_='item-wrap')
            if property_listings == old_property_listings:
                print('fim de scrape')
                break

        for property_listing in property_listings:
                property_info = extract_property_info(property_listing)
                full_property_info.append(property_info)
        #now i do a dataframe with the full_property_info, and a column with the name 'Junqueira' and the date of today
    df = pd.DataFrame(full_property_info)
    #dropa linhas com a coluna price vazia
    df = df.dropna(subset=['preco'])
    df = df.fillna(0)
    try:
        #converte a coluna price para float
        df['preco'] = df['preco'].astype(float)
        df['preco'] = df['preco']/100
        #converte a coluna area para float
        df['area'] = df['area'].astype(float)
        #divido a area por 1000 e arredondo uma casa para todos os valores da coluna area
        df['area'] = round(df['area']/100, 1)
        #converte valores de quartos, vagas e banheiros para int
        df['quartos'] = df['quartos'].astype(int)
        df['vagas'] = df['vagas'].astype(int)
        df['banheiros'] = df['banheiros'].astype(int)
    except:
        print('erro na conversão de tipos junqueira')
        pass
    df['Imobiliaria'] = 'Junqueira'
    df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df = df[['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro', 'Data_scrape']]
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a', header = False)
    return 1
