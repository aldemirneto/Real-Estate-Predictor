import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import json
import shap
from xgboost import XGBRegressor

st.sidebar.markdown("""
# 🏠 Predição de Preço de Imóvel

Nesta página, você poderá obter uma estimativa do preço de um imóvel com base em suas características.

## Características do Imóvel

Para realizar a predição do preço, serão consideradas as seguintes características do imóvel:

- Área do imóvel
- Número de quartos
- Número de banheiros
- Número de vagas de estacionamento

## Modelo de Machine Learning

Utilizamos um modelo de Machine Learning treinado com dados de imóveis para fazer a predição do preço. O modelo aprendeu padrões nos dados e pode fornecer uma estimativa com base nas características fornecidas.

## Como Usar

1. Preencha as características do imóvel nos campos à direita.
2. Clique no botão "Prever" para obter a estimativa do preço.
3. O resultado será exibido na página principal.

## Limitações

É importante ressaltar que essa estimativa é baseada em dados históricos e em um modelo preditivo. O preço real do imóvel pode variar de acordo com fatores externos e condições do mercado imobiliário.

## Conclusão

Essa página foi criada para ajudar usuários a terem uma ideia aproximada do preço de um imóvel com base em suas características. Lembre-se de considerar outros fatores relevantes ao tomar decisões relacionadas à compra ou venda de um imóvel.

""")

st.markdown(
    """
    <style>

    h1, h2{
        color: #3b5998;
    }
    h2 {
        margin-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Function to load the XGBoost model
@st.cache_resource()
def load_model():
    xgb_model = XGBRegressor()
    xgb_model.load_model('Model/xgb_model.json')
    return xgb_model


# Load the XGBoost model
xgb_model = load_model()

# Load the neighborhood encoding mapping
with open('Model/neighborhood_encoding.json', 'r') as f:
    neighborhood_encoding = json.load(f)


# Function to preprocess input data
def preprocess_input(data):
    # Create a DataFrame from the input data
    df = pd.DataFrame([data])

    # Encode the neighborhood using the loaded mapping
    df['bairro_encoded'] = df['bairro'].map(neighborhood_encoding)
    #
    # Reorder the columns to match the training data
    df = df[['area', 'quartos', 'vagas', 'banheiros', 'bairro_encoded']]

    return df


# Function to predict prices using the loaded model
def predict_prices(data):
    input_data = preprocess_input(data)
    predictions = np.exp(xgb_model.predict(input_data))
    return predictions


st.title('Real Estate Price Prediction')
st.markdown("---")

# Load the dataset to get the unique neighborhood values
df = pd.read_csv('imoveis.csv', sep=';')
neighborhoods = df['bairro'].unique().tolist()

#
selected_neighborhoods = st.selectbox('Select Neighborhood(s)', neighborhoods)
area = st.number_input('Area (in square meters)', min_value=0)
bedrooms = st.number_input('Number of bedrooms', min_value=0)
bathrooms = st.number_input('Number of bathrooms', min_value=0)
parking_spaces = st.number_input('Number of parking spaces', min_value=0)

# Prepare input data
input_data = {
    'bairro': selected_neighborhoods,
    'area': area,
    'quartos': bedrooms,
    'vagas': parking_spaces,
    'banheiros': bathrooms
}

# Make the prediction
if st.button('Predict'):
    explainer = shap.Explainer(xgb_model)
    shap_values = explainer(preprocess_input(input_data))

    # Create a summary plot

    prediction = predict_prices(input_data)

    st.subheader('Preço Estimado')
    # write the price in thousands with 2 decimals

    st.success(f"O Preço do seu imóvel é R${prediction[0] / 1000:.3f} mil reais")
    st.markdown("---")

    st.title("Interpretação Abrangente do Modelo")

    st.subheader('Entendendo a Importância das Características')
    st.write('''
    Quando treinamos um modelo de IA, ele aprende a tomar decisões com base nas informações fornecidas por diferentes características ou variáveis. Essas características podem ser coisas como idade, gênero, renda, entre outras, dependendo do problema que o modelo está tentando resolver.
    Ao analisar o modelo e interpretar suas previsões, podemos querer entender quais características têm mais influência nos resultados. Isso nos ajuda a entender como o modelo está tomando suas decisões e quais aspectos são mais importantes para o resultado final.
    Uma maneira de visualizar essa importância é por meio de gráficos. O gráfico de enxame de abelhas, por exemplo, mostra a distribuição dos impactos de cada característica em diferentes exemplos. Cada ponto no gráfico representa um exemplo, e a posição ao longo do eixo vertical indica o impacto daquela característica na previsão. Quanto mais acima o ponto estiver, maior é o impacto positivo da característica. Por outro lado, quanto mais abaixo o ponto estiver, maior é o impacto negativo da característica.       
    ''')

    fig1, ax1 = plt.subplots()
    shap.summary_plot(shap_values, show=False)
    plt.xlabel('Valor SHAP (Impacto na Saída do Modelo)')
    st.pyplot(fig1)

    st.markdown("---")

    st.subheader('Analisando as Contribuições Individuais das Características')
    st.write(
        '''
        No contexto da aplicação, o gráfico de cascata ajudar a entender como cada característica contribui para a previsão final. Cada valor no gráfico de cascata representaria a contribuição individual de uma característica específica para o preço do imóvel.
        Por exemplo, se considerarmos a característica "bairro_encoded" com um valor de +0,43, isso indicaria que, em média, propriedades localizadas nesse bairro têm uma contribuição positiva de 0,43 unidades monetárias para o preço do imóvel. Isso significa que estar nesse bairro específico tende a aumentar o preço do imóvel em comparação com um valor de referência, como a média geral dos preços.
        A magnitude dos valores seria uma indicação da força de influência de cada característica.
        Por exemplo, um valor maior para "área" sugeriria que a dimensão do imóvel tem uma contribuição mais significativa para o preço em comparação com outras características.
        
    ''')

    fig2, ax2 = plt.subplots()
    shap.waterfall_plot(shap_values[0], show=False)
    plt.title('Contribuições Individuais das Características')
    st.pyplot(fig2)

    st.write('''
    Essas visualizações e interpretações nos ajudam a entender quais características são mais relevantes para o modelo e como elas afetam as previsões. Com essa compreensão, podemos fazer ajustes ou melhorias no modelo, se necessário, para garantir que ele esteja levando em consideração as características mais importantes para a tomada de decisões.
    ''')

# Attribution
st.markdown("---")
st.write("Built with ❤️ by Aldemir")
st.write("Check out my [GitHub](https://github.com/aldemirneto)")
