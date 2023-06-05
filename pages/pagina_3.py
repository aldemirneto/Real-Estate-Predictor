import _thread

import numpy as np
import pandas as pd
import streamlit as st
import json
from xgboost import XGBRegressor


# Function to load the XGBoost model
@st.cache_resource()
def load_model():
    xgb_model = XGBRegressor()
    xgb_model.load_model(st.secrets['model']['MODEL'])
    return xgb_model


# Load the XGBoost model
xgb_model = load_model()

# Load the neighborhood encoding mapping
with open(st.secrets['encoding']['NEIGHBORHOOD_ENCODING'], 'r') as f:
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
    print('Predicting prices...')
    input_data = preprocess_input(data)
    predictions = np.exp(xgb_model.predict(input_data))
    return predictions




st.title('Real Estate Price Prediction')
st.markdown("---")

# Load the dataset to get the unique neighborhood values
df = pd.read_csv('imoveis.csv', sep=';')
neighborhoods = df['bairro'].unique().tolist()

# Sidebar
st.sidebar.title("Input Features")
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
    prediction = predict_prices(input_data)
    print(prediction)
    st.subheader('Price Prediction')
    #write the price in thousands with 2 decimals


    st.success(f"O Preço do seu imóvel é R${prediction[0]/1000:.3f} mil reais")

# App description
st.markdown("---")
st.subheader('About')
st.write(
    "This app predicts real estate prices based on input features such as neighborhood, area, number of bedrooms, number of bathrooms, and number of parking spaces. Adjust the input values in the sidebar and click 'Predict' to get the price prediction.")

# Attribution
st.markdown("---")
st.write("Built with ❤️ by Aldemir")
st.write("Check out my [GitHub](https://github.com/aldemirneto)")
