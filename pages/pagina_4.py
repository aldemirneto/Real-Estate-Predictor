import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Read the dataset
data = pd.read_csv('imoveis.csv', sep=';')
#
# # Set page title
# st.title('Analise e Visualização de Dados')
#
# # Chart 1: Histogram of Prices, with edgecolor black, instead of 1e^7, show as 10,000,000
# st.subheader('Histograma de Preços')
# fig, ax = plt.subplots()
# ax.hist(data['preco'], bins=10, edgecolor='black')
# st.pyplot(fig)
#
#
#
# # Chart 2: Scatter Plot: Price vs. Area with an no transparency, edgecolor black, instead of 1e^7, show as 10,000,000 and an correlation line
# st.subheader('Preço vs. Área')
# # Create the scatter plot
# fig, ax = plt.subplots()
# ax.scatter(data['area'], data['preco'], alpha=0.5, edgecolor='black')
# ax.set(xlabel='Preço', ylabel='Área',
#        title='Preço vs. Área')
# st.pyplot(fig)
#
#
#
# Chart 3: Bar Chart: Number of Properties by Number of Rooms

fig, ax = plt.subplots()
ax.bar(sorted(data['quartos'].unique().tolist()), data['quartos'].value_counts())
ax.set(xlabel='Numero de quartos', ylabel='Numero de imoveis',
       title='Numero de imoveis por numero de quartos')
st.pyplot(fig)


# # Chart 4: Bar Chart: Number of Properties by Number of Bathrooms
fig, ax = plt.subplots()
#get the unique values of bathrooms and order them
bathrooms = sorted(data['banheiros'].unique().tolist())

value_counts = data['banheiros'].value_counts()

print(bathrooms, value_counts)
#plot the bar chart
ax.bar(bathrooms, value_counts)

ax.set(xlabel='Numero de banheiros', ylabel='Numero de imoveis', title='Numero de imoveis por numero de banheiros')
st.pyplot(fig)

# Chart 5: Bar Chart: Number of Properties by Number of Parking Spaces adding title and labels and description and making it interactive
fig, ax = plt.subplots()
parking_counts = data['vagas'].dropna().value_counts()
ax.bar(parking_counts.index, parking_counts)
ax.set(xlabel='Numero de vagas', ylabel='Numero de imoveis',
       title='Numero de imoveis por numero de vagas')
st.pyplot(fig)

#Chart 6: normal distribution of prices, with a title and labels and description and making it interactive, make the bins 20
st.subheader('Distribuição Normal de Preços')
fig, ax = plt.subplots()
ax.hist(data['preco'], bins=20, edgecolor='black', density=True)
ax.set(xlabel='Price', ylabel='Density', title='Distribution of Prices')
st.pyplot(fig)

st.markdown('''
# Distribuição Assimétrica e Tratamento Logarítmico

Uma distribuição assimétrica ocorre quando os valores de um conjunto de dados estão deslocados em relação à média ou mediana, resultando em uma forma assimétrica. Existem dois tipos principais de distribuição assimétrica:

- **Distribuição Assimétrica Positiva:** Também conhecida como distribuição assimétrica para a direita, é caracterizada por uma cauda longa à direita e uma concentração de valores à esquerda da média. Nesse caso, a mediana é menor que a média.

Exemplo: O gráfico acima, que mostra a distribuição de preços dos imóveis, é um exemplo de distribuição assimétrica positiva.

- **Distribuição Assimétrica Negativa:** Também chamada de distribuição assimétrica para a esquerda, é caracterizada por uma cauda longa à esquerda e uma concentração de valores à direita da média. Nesse caso, a mediana é maior que a média.

Exemplo: Considere um conjunto de dados que represente o tempo de reação de um grupo de pessoas a um estímulo. Se algumas pessoas tiverem tempos de reação muito curtos, isso pode resultar em uma distribuição assimétrica negativa.

## Tratamento Logarítmico

Em alguns casos, é necessário realizar um tratamento logarítmico em uma distribuição assimétrica para garantir a integridade do modelo estatístico. Esse tratamento é especialmente útil quando a assimetria está relacionada a valores extremamente altos ou baixos.

O uso do tratamento logarítmico ajuda a reduzir a magnitude dos valores extremos e aproxima a distribuição de uma forma mais simétrica, facilitando a interpretação dos resultados e a aplicação de técnicas estatísticas.

Por exemplo, ao aplicar o tratamento logarítmico a uma distribuição assimétrica positiva, os valores extremamente altos são reduzidos, aproximando-se mais da média e reduzindo a influência desses valores extremos na análise.

É importante ressaltar que o tratamento logarítmico deve ser aplicado com cautela e apenas quando faz sentido em relação ao contexto do problema. Além disso, é fundamental que sejam feitas análises adicionais para validar a adequação do tratamento logarítmico aos dados.

Em resumo, ao se deparar com uma distribuição assimétrica, o tratamento logarítmico pode ser uma técnica útil para transformar a distribuição e melhorar a interpretação e análise dos dados, especialmente quando há presença de valores extremos.

''')
#Chart 7: normal distribution after log transformation of prices, with a title and labels and description and making it interactive, only for prices > 0
st.subheader('Distribuição Normal de Preços (Pós Transformação Logarítmica)')
fig, ax = plt.subplots()
ax.hist(np.log(data[data['preco'] > 0]['preco']), bins=10, edgecolor='black', density=True)
ax.set(xlabel='Price', ylabel='Density', title='Distribution of Prices')
st.pyplot(fig)

#Chart8: normal distribution of areas, with a title and labels and description and making it interactive, make the bins 20
st.subheader('Distribuição Normal de Áreas')
# taking the outliers out
data = data[data['area'] < data['area'].quantile(0.99)]
fig, ax = plt.subplots()
ax.hist(data['area'], bins=10, edgecolor='black', density=True)
ax.set(xlabel='Area', ylabel='Density', title='Distribution of Areas')
st.pyplot(fig)
