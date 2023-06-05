import scipy.stats as stats
import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
# Read the dataset
data = pd.read_csv('imoveis.csv', sep=';')
#
# # Set page title
# st.title('Analise e Visualização de Dados')
#
# # Chart 1: Histogram of Prices, with edgecolor black, instead of 1e^7, show as 10,000,000
fig = go.Figure(data=[go.Histogram(x=data['preco'], marker_color='#EB89B5', opacity=0.75)])
fig.update_layout(title_text='Histograma de Preços', xaxis_title_text='Preço', yaxis_title_text='Contagem')
st.plotly_chart(fig, use_container_width=True)


# # Chart 2: Scatter Plot: Price vs. Area with an no transparency, edgecolor black, instead of 1e^7, show as 10,000,000 and an correlation line

# Create the scatter plot
fig = go.Figure(data=go.Scatter(x=data['area'], y=data['preco'], mode='markers'))

# Update axes lines
fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
# Update chart layout
fig.update_layout(
    title='Preço vs. Área',
    xaxis_title='Área',
    yaxis_title='Preço')
# Show chart
st.plotly_chart(fig)


# Chart 3: Bar Chart: Number of Properties by Number of Rooms
fig = go.Figure(data=[go.Bar(x=sorted(data['quartos'].unique().tolist()), y=data['quartos'].value_counts())])
fig.update_layout(title='Número de Propriedades por Número de Quartos',
                     xaxis_title='Número de Quartos',
                        yaxis_title='Número de Propriedades')
st.plotly_chart(fig)


# # Chart 4: Bar Chart: Number of Properties by Number of Bathrooms


bathrooms = sorted(data['banheiros'].unique().tolist())
value_counts = data['banheiros'].value_counts()
fig = go.Figure(data=[go.Bar(x=bathrooms, y=value_counts)])
fig.update_layout(title='Numero de imoveis por numero de banheiros',
                    xaxis_title='Numero de banheiros',
                    yaxis_title='Numero de imoveis')
st.plotly_chart(fig)



# Chart 5: Bar Chart: Number of Properties by Number of Parking Spaces adding title and labels and description and making it interactive

parking_counts = data['vagas'].dropna().value_counts()

fig = go.Figure(data=[go.Bar(x=parking_counts.index, y=parking_counts)])
fig.update_layout(title='Numero de imoveis por numero de vagas de garagem',
                     xaxis_title='Numero de vagas de garagem',
                        yaxis_title='Numero de imoveis')
st.plotly_chart(fig)

# Calculate mean and median
mean_price = np.mean(data['preco'])
median_price = np.median(data['preco'])
std_price = np.std(data['preco'])
# Chart 6: Normal Distribution of Prices displaying the quartiles
# Calculate mean, median, and quantiles

quantiles = np.percentile(data['preco'], [1,25, 50, 75, 99])

# Chart 6: Normal Distribution of Prices
#the linspace should be between the 1% quantile and the 99% quantile

x = np.linspace(quantiles[0], quantiles[-1], 100)
y = stats.norm.pdf(x, mean_price, std_price)
# Create the figure using Plotly graph objects
fig = go.Figure()

## Add the normal distribution curve
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Curva Normal', line=dict(color='blue')))

# Add vertical lines for mean and quantiles using go.Line
fig.add_trace(go.Scatter(x=[mean_price, mean_price], y=[0, max(y)],
                         mode='lines', name='Média', line=dict(color='red', dash='dash')))

fig.add_trace(go.Scatter(x=[quantiles[0], quantiles[0]], y=[0, max(y)],
                         mode='lines', name='1º Percentil', line=dict(color='green', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[1], quantiles[1]], y=[0, max(y)],
                         mode='lines', name='25º Percentil', line=dict(color='blue', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[2], quantiles[2]], y=[0, max(y)],
                         mode='lines', name='50º Percentil', line=dict(color='orange', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[3], quantiles[3]], y=[0, max(y)],
                         mode='lines', name='75º Percentil', line=dict(color='pink', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[4], quantiles[4]], y=[0, max(y)],
                         mode='lines', name='99º Percentil', line=dict(color='purple', dash='dash')))

# Update layout and axis labels
fig.update_layout(title='Distribuição de Preços',
                  xaxis_title='Preço',
                  yaxis_title='Densidade')

# Display the plot
st.plotly_chart(fig)


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
# Filter data for prices greater than 0
filtered_data = data[data['preco'] > 0]

# Calculate the log-transformed prices
log_prices = np.log(filtered_data['preco'])



# Generate data for the normal distribution curve

# Calculate the mean, median, and quantiles of log-transformed prices
mean_log_price = np.mean(log_prices)

std_log_price = np.std(log_prices)
quantiles_log_price = np.percentile(log_prices, [1, 25, 50, 75, 99])

x = np.linspace(quantiles_log_price[0], quantiles_log_price[-1], 100)
y = stats.norm.pdf(x, mean_log_price, std_log_price)
# Create the figure using Plotly graph objects
fig = go.Figure()

## Add the normal distribution curve
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Curva Normal', line=dict(color='blue')))

# Add vertical lines for mean and quantiles using go.Line
fig.add_trace(go.Scatter(x=[mean_log_price, mean_log_price], y=[0, max(y)],
                         mode='lines', name='Média', line=dict(color='red', dash='dash')))

fig.add_trace(go.Scatter(x=[quantiles_log_price[0], quantiles_log_price[0]], y=[0, max(y)],
                         mode='lines', name='1º Percentil', line=dict(color='green', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[1], quantiles_log_price[1]], y=[0, max(y)],
                         mode='lines', name='25º Percentil', line=dict(color='blue', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[2], quantiles_log_price[2]], y=[0, max(y)],
                         mode='lines', name='50º Percentil', line=dict(color='orange', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[3], quantiles_log_price[3]], y=[0, max(y)],
                         mode='lines', name='75º Percentil', line=dict(color='pink', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[4], quantiles_log_price[4]], y=[0, max(y)],
                         mode='lines', name='99º Percentil', line=dict(color='purple', dash='dash')))

# Update layout and axis labels
fig.update_layout(title='Distribuição de Preços transformados em Log',
                  xaxis_title='Preço (Transformação Logarítmica)',
                  yaxis_title='Densidade')


# Display the plot
st.plotly_chart(fig)

