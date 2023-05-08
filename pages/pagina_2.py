import streamlit as st
import folium
import pandas as pd
import json
from streamlit_folium import st_folium



st.sidebar.markdown("""
# 🗺️ 

Nesta página, você encontrará dados sobre cada bairro de Piracicaba, representados no mapa com o preço médio de venda de imóvel em cada um deles.

## Visualização no Mapa

Utilizando dados geoespaciais, é possível visualizar no mapa os bairros de Piracicaba e o preço médio de venda de imóvel em cada um deles. Essa visualização é útil para entender como o mercado imobiliário está distribuído na cidade.

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
df = pd.read_csv('imoveis.csv', sep=';')
#from this df, create a new df with the avg price per neighborhood
df_bairros = df.groupby('bairro').agg({'preco': 'mean'}).reset_index()
df_bairros.columns = ['bairro', 'preco_medio']


print(df_bairros['bairro'])
# Informações dos bairros de Piracicaba
bairros = data['bairros']['features']

# Cria um DataFrame com as informações dos imóveis em cada bairro
dados = []
for bairro in bairros:
    nome = bairro['properties']['name']

    preco_medio = round((df_bairros.loc[df_bairros['bairro'] == nome, 'preco_medio'].values[0]/1000000), 2) if df_bairros.loc[df_bairros['bairro'] == nome, 'preco_medio'].any() else 0

    dados.append({'Bairro': nome, 'preco_medio': preco_medio})
df = pd.DataFrame(dados)


# Criação do mapa
m = folium.Map(location=[lat, lon], zoom_start=12)

# Adiciona marcadores para cada bairro
for bairro in bairros:
    nome = bairro['properties']['name']
    coords = bairro['properties']['centroid']
    preco_medio_values = df.loc[df['Bairro'] == nome, 'preco_medio'].values
    tooltip = f"Preço médio venda bairro {nome.replace('_', ' ')}<br>" \
              f"<div style='text-align: center;'>{preco_medio_values[0] if len(preco_medio_values) > 0 else 'N/A'} milhões de reais</div>"

    folium.Marker(
        location=[coords[1], coords[0]],
        tooltip=tooltip,
    ).add_to(m)

choropleth = folium.Choropleth(
    geo_data=data['bairros'],
    data=df,
    columns=['Bairro', 'preco_medio'],
    key_on='feature.properties.name',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Preço Médio por bairro'
).add_to(m)

# # Renderiza o mapa no Streamlit
st_folium(m)
