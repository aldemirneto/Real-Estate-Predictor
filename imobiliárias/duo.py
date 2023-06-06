import time
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
        elif 'Banheiro' in i.text:
            banheiros = i.text
            banheiros = banheiros.replace('Banheiros', '').replace('Banheiro', '').replace(' ', '') if banheiros else None
        elif 'Vaga' in i.text:
            vagas = i.text
            vagas = vagas.replace('Vagas', '').replace('Vaga', '').replace(' ', '') if vagas else None
        elif 'm²' in i.text:
            area = i.text
            area = area.replace('m²', '').replace(' ', '') if area else None

    location = property_html.find('h3')
    location = location.text.strip() if location else 'Sem Bairro'
    #Reserva das Paineiras - Piracicaba - SP i want to get untill the first '-'
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







def run():
    urls = ['https://www.duoimoveis.com.br/imoveis/a-venda/piracicaba?pagina=']
    full_property_info = []
    for url in urls:
        for i in range(1, 300):
            time.sleep(2)
            page_content = None
            old_page_content = None
            try:
                page_content = get_page_content(
                    f'{url}{i}')
                if i > 1:
                    old_page_content = get_page_content(f'{url}{i-1}')

            except Exception as e:
                print(e)
                print('fim de scrape')


            property_listings = page_content.find_all('a', class_='card-with-buttons borderHover')
            if old_page_content:
                old_property_listings = old_page_content.find_all('a', class_='card-with-buttons borderHover')
                if property_listings == old_property_listings:
                    print('fim de scrape')
                    break

            for property_listing in property_listings:
                    link = property_listing['href']
                    property = property_listing.find('div', class_='card-with-buttons__footer')
                    property_info = extract_property_info(property, f'https://www.duoimoveis.com.br{link}?from=sale')
                    full_property_info.append(property_info)

        #now i do a dataframe with the full_property_info, and a column with the name 'Junqueira' and the date of today
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
    df['last-seen'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df = df[['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro', 'Data_scrape', 'last-seen']]
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a',  header=False)
    return 1


run()