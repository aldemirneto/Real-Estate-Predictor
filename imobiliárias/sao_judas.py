import requests
from bs4 import BeautifulSoup
import pandas as pd
def get_page_content(request_url):
    # faz o request
    page_response = requests.get(request_url, timeout=5)
    # retorna o conteúdo da página em html
    return BeautifulSoup(page_response.content, "html.parser")


def extract_property_info(property_html, link):
    quartos = None
    vagas = None
    banheiros = None
    area = None
    price = None
    location = 'Sem Bairro'
    info_list = property_html.find_all('ul')
    for info in info_list:
        info = info.find_all('p', class_='infos')
        for i in info:
            #if the string 'Quartos' is in the element, i want to get the span element that is next to it
            if 'Quartos' in i.text:
                quartos = i.find_next('span').text
                quartos = quartos.replace(' ', '') if quartos else None
            elif 'Banheiros' in i.text:
                banheiros = i.find_next('span').text
                banheiros = banheiros.replace(' ', '') if banheiros else None
            elif 'Garagens' in i.text:
                vagas = i.find_next('span').text
                vagas = vagas.replace(' ', '') if vagas else None
            elif 'Área útil' in i.text:
                area = i.find_next('span').text
                area = area.replace('m2', '').replace(' ', '') if area else None
            elif 'Área Total' in i.text:
                area = i.find_next('span').text
                area = area.replace('m2', '').replace(' ', '') if area else None
            elif 'Preço' in i.text:
                price = i.find_next('span').text
                price = float(price.replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '').replace('\n', '').replace(',00', '')) if price else None
            elif 'Bairro' in i.text:
                location = i.find_next('span').text.strip()

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
    urls = ['https://www.imobiliariasjudas.com.br/venda-de-casa/', 'https://www.imobiliariasjudas.com.br/venda-de-apartamento/', 'https://www.imobiliariasjudas.com.br/venda-de-imovel-comercial/']
    full_property_info = []
    for url in urls:
        for i in range(0, 20, 20):

            page_content = None
            old_page_content = None
            try:
                page_content = get_page_content(
                    f'{url}{i}')
                if i > 1:
                    old_page_content = get_page_content(f'{url}{i-1}')

            except:
                print('fim de scrape')


            property_listings = page_content.find_all('p', class_='readmore text-right')
            if old_page_content:
                old_property_listings = old_page_content.find_all('p', class_='readmore text-right')
                if property_listings == old_property_listings:
                    print('fim de scrape')
                    break

            for property_listing in property_listings:
                    property = get_page_content(property_listing.find('a')['href'])
                    property = property.find('div', class_='prop_addinfo')
                    property_info = extract_property_info(property, property_listing.find('a')['href'])
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
    df['Imobiliaria'] = 'Sâo Judas'
    df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df = df[['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro', 'Data_scrape']]
    df.to_csv('imoveis.csv', index=False, sep=';', mode='a',  header=False)
    return 1


