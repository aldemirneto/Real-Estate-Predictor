from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from st_aggrid import AgGrid

st.sidebar.markdown("""
# 📊 

Nesta página, você encontrará dados detalhados sobre os imóveis em cada bairro de Piracicaba, incluindo informações como:

- Número de quartos
- Número de banheiros
- Número de vagas de garagem
- Preço do imóvel

## Análise de Dados

Com esses dados, é possível fazer análises mais aprofundadas sobre cada bairro e suas propriedades, como a média de preços, a distribuição dos tipos de imóveis em cada bairro, entre outras informações relevantes para compradores, vendedores e investidores no mercado imobiliário.

## Utilização

Essas informações podem ser usadas para entender melhor o mercado imobiliário em Piracicaba, ajudando os usuários a tomar decisões informadas na compra, venda ou investimento em imóveis na cidade.

## Conclusão

Esta página fornece informações detalhadas sobre os imóveis em cada bairro de Piracicaba. Com essas informações, esperamos ajudar os usuários a entenderem melhor o mercado imobiliário e tomarem decisões mais informadas. 

 
""")


df = pd.read_csv('imoveis.csv', sep=';')
# Exibindo as primeiras linhas do DataFrame

bairro_options = df['bairro'].unique()
bairro = st.selectbox("Selecione o bairro", sorted([x.replace('_', ' ') for x in bairro_options]))
quartos = st.selectbox("Selecione o numero minimo de quartos",[i for i in range(10)])
banheiros = st.selectbox("Selecione o numero minimo de banheiros",[i for i in range(10)])


def cor_sinc(df):
    ultima_data_scrape = df['Data_scrape'].max()
    ultima_data_scrape = datetime.strptime(ultima_data_scrape, '%Y-%m-%d').date()
    today = datetime.today().date()
    diff = today - ultima_data_scrape
    if diff <= timedelta(days=1):
        return '#a8d8b9'  # green
    elif diff <= timedelta(days=3):
        return '#f3d38c'  # yellow
    elif diff <= timedelta(days=5):
        return '#f9b4ab'  # red

bg = cor_sinc(df)
st.markdown(f"""<div style= 'background-color: rgba({int(bg[1:3], 16)}, {int(bg[3:5], 16)}, {int(bg[5:7], 16)}, 0.3);
                            backdrop-filter: blur(10px);
                            box-shadow: 0 8px 32px 0 rgba({int(bg[1:3], 16)}, {int(bg[3:5], 16)}, {int(bg[5:7], 16)}, 0);
                            border-radius: 10px;
                            text-align: center;border-radius: 7px;
                            padding-left: 12px;
                            padding-top: 18px;
                            padding-bottom: 18px;'>"""
            f"Ultimo Scrape: {df['Data_scrape'].max()}"
            "</div>", unsafe_allow_html=True)

resultados = df[(df['bairro'] == bairro.replace(' ', '_')) & (df['quartos'] >= quartos) & (df['banheiros'] >= banheiros)]
resultados = resultados.drop_duplicates(subset=['link'])
resultados_sem_data_scrape = resultados.drop(['Data_scrape', 'bairro', 'last_seen'], axis=1).reset_index(drop=True)

num_columns = len(resultados_sem_data_scrape.columns)

# Calculate the maximum width for each column
max_column_width = 100 / num_columns  # Assuming an equal width distribution

# Create a list of column definitions with the maximum width
column_defs = []
for column_name in resultados_sem_data_scrape.columns:
    column_def = {"headerName": column_name, "field": column_name, "width": max_column_width}
    column_defs.append(column_def)

# Set the column definitions and other options
grid_options = {
    "theme": "alpine",
    "allow_unsafe_jscode": True,
    "columnDefs": column_defs
}

AgGrid(resultados_sem_data_scrape, grid_options=grid_options)

