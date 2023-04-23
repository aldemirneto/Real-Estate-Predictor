import streamlit as st

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


import pandas as pd
import numpy as np

# Criando um array aleatório com números de quartos, banheiros e preços
num_imoveis = 50
num_quartos = np.random.randint(1, 5, num_imoveis)
num_banheiros = np.random.randint(1, 4, num_imoveis)
bairros = ['Centro', 'Pauliceia', 'Alto', 'Vila Rezende', 'Nova América', 'Santa Terezinha']
local = np.random.choice(bairros, num_imoveis)
precos = np.random.randint(50000, 500000, num_imoveis)

# Criando o DataFrame
imoveis = pd.DataFrame({
    'Quartos': num_quartos,
    'Banheiros': num_banheiros,
    'Bairro': local,
    'Preço': precos
})

# Exibindo as primeiras linhas do DataFrame
print(imoveis.head())

bairro = st.selectbox("Selecione o bairro",['Centro', 'Pauliceia', 'Alto', 'Vila Rezende', 'Nova América', 'Santa Terezinha'])
quartos = st.selectbox("Selecione o numero minimo de quartos",[i for i in range(10)])
banheiros = st.selectbox("Selecione o numero minimo de banheiros",[i for i in range(10)])

st.table(imoveis[(imoveis['Bairro'] == bairro) & (imoveis['Quartos'] >= quartos) & (imoveis['Banheiros'] >= banheiros)] )