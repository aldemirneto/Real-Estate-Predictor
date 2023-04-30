import streamlit as st
import pandas as pd

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


resultados = df[(df['bairro'] == bairro.replace(' ', '_')) & (df['quartos'] >= quartos) & (df['banheiros'] >= banheiros)]
resultados_sem_data_scrape = resultados.drop('Data_scrape', axis=1).reset_index(drop=True)
st.write(resultados_sem_data_scrape[['preco', 'area', 'quartos', 'banheiros', 'vagas','link', 'Imobiliaria']])
