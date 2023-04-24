import streamlit as st
import folium
import pandas as pd
import json
from streamlit_folium import st_folium


st.sidebar.markdown("""

# 🗺️ 

Nesta página, você encontrará dados sobre cada bairro de Piracicaba, representados no mapa com a quantidade de imóveis em cada um deles.

## Visualização no Mapa

Utilizando dados geoespaciais, é possível visualizar no mapa os bairros de Piracicaba e a quantidade de imóveis em cada um deles. Essa visualização é útil para entender como o mercado imobiliário está distribuído na cidade.

## Análise de Dados

Com base nos dados coletados, é possível fazer análises mais aprofundadas sobre cada bairro, como a média de preços, tipos de imóveis mais comuns, etc. Essas informações são valiosas para compradores, vendedores e investidores no mercado imobiliário.

## Conclusão

Esta página fornece uma visão geral dos dados de cada bairro de Piracicaba no mapa. Com essas informações, esperamos ajudar os usuários a entenderem melhor o mercado imobiliário e tomarem decisões mais informadas.

    
""")

# Lê o arquivo GeoJSON com as coordenadas da cidade de Piracicaba e de seus bairros
with open('piracicaba.json', 'r') as f:
    data = json.load(f)


# Coordenadas da cidade de Piracicaba
lat, lon = data['piracicaba']['geometry']['coordinates'][::-1]

# Informações dos bairros de Piracicaba
bairros = data['bairros']['features']

# Cria um DataFrame com as informações dos imóveis em cada bairro
dados = []
for bairro in bairros:
    nome = bairro['properties']['name']
    imoveis = bairro['properties']['imoveis']
    dados.append({'Bairro': nome, 'Imoveis': imoveis})
df = pd.DataFrame(dados)


# Criação do mapa
m = folium.Map(location=[lat, lon], zoom_start=12)

# Adiciona marcadores para cada bairro
for bairro in bairros:
    nome = bairro['properties']['name']
    coords = bairro['properties']['centroid']
    tooltip = f"{nome}: {df.loc[df['Bairro'] == nome, 'Imoveis'].values[0]} imóveis"
    folium.Marker(
        location=[coords[1], coords[0]],  # inverte a ordem das coordenadas
        tooltip=tooltip,
    ).add_to(m)


choropleth = folium.Choropleth(
    geo_data=data['bairros'],
    data=df,
    columns=['Bairro', 'Imoveis'],
    key_on='feature.properties.name',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Quantidade de Imóveis'
).add_to(m)

# # Renderiza o mapa no Streamlit
st_folium(m)
