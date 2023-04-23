import requests
from bs4 import BeautifulSoup


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
            quartos = info.find('span').text.strip()
        elif 'Vaga' in info.text:
            vagas = info.find('span').text.strip()
        elif 'Banheiro' in info.text:
            banheiros = info.find('span').text.strip()


    price_element = property_html.find('p', class_='price')
    price = price_element.text.strip() if price_element else None

    area_element = property_html.find('li').find('span')
    area = area_element.text.strip() if area_element else None

    location_element = property_html.find('p', class_='neighborhood-city-titles')
    location = location_element.text.strip() if location_element else None

    return {
        'price': price,
        'area': area,
        'quartos': quartos,
        'vagas': vagas,
        'banheiros': banheiros,

        'location': location
    }


for i in range(300):
    try:
        page_content = get_page_content(
            f'https://www.friasneto.com.br/imoveis/todos-os-imoveis/comprar-ou-alugar/piracicaba/?locacao_venda=V&id_cidade=2&pag={i}')
    except:
        print('fim de scrape')
        break
    property_listings = page_content.find_all('div', class_='col-xs-12 col-sm-4 col-md-3 container-enterprises-item')

    for property_listing in property_listings:

        property_info = extract_property_info(property_listing)
        print(property_info)
        print('---------------------')
