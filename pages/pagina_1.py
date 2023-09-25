import time
from datetime import datetime, timedelta
from streamlit_modal import Modal
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
# Tipo = st.selectbox("Selecione o tipo do imóvel", ['Casa', 'Apartamento', 'Terreno', 'Comercial', 'Rural', 'Flat', 'Loft', 'Studio'])

# Create 4 columns to place the widgets
col1, col2, col3, col4 = st.columns(4)

# Dropdowns for rooms in Column 1
# Number input for rooms in Column 1
quartos = col1.number_input("Mínimo de quartos", min_value=0, max_value=10, value=0, step=1)

# Number input for bathrooms in Column 2
banheiros = col2.number_input("Mínimo de banheiros", min_value=0, max_value=9, value=0, step=1)

# Number input for parking spots in Column 3
vagas = col3.number_input("Mínimo de vagas", min_value=0, max_value=9, value=0, step=1)

# Number input for price in Column 4
area = col4.number_input('Área mínima em m2', min_value=0, max_value=1000, value=0, step=10)

# Slider for area below the columns since it might be more visually appealing as a wider widget
preco = st.slider("Preço máximo", min_value=0, max_value=1000000, value=100000, step=50000)



# Inicialização do modal
modal_alerta = Modal("Criar Alerta", key="modal_alerta_key")

# Botão para abrir o modal
btn_criar_alerta = st.button("Deseja ser notificado quando novos imóveis correspondentes aos critérios acima estiverem disponíveis?")
if btn_criar_alerta:
    modal_alerta.open()

st.markdown(
    f"""
    <style>
    div[data-modal-container='true'][key='{modal_alerta.key}'] {{
        width: calc(100vw - 300px) !important;  <!-- Ajusta a largura -->
        left: 300px !important; <!-- Posiciona o modal após a barra lateral -->
    }}

    div[data-modal-container='true'][key='{modal_alerta.key}'] > div:first-child > div:first-child {{
        background-color: black !important;  <!-- Cor de fundo do modal em preto -->
        color: #eee !important;  <!-- Cor do texto do modal em modo escuro -->
    }}

    div[data-modal-container='true'][key='{modal_alerta.key}']::before {{
        background-color: rgba(0, 0, 0, 0.5) !important;  <!-- Cor do fundo semi-transparente em preto -->
    }}
    </style>
    """,
    unsafe_allow_html=True
)
# Conteúdo do modal
if modal_alerta.is_open():

    with modal_alerta.container():
        st.write(
            "Informe seu e-mail para receber notificações sobre novos imóveis que correspondam aos seus critérios de busca.")

        # Campo para inserção do e-mail
        email = st.text_input("Endereço de E-mail")
        # Botão de confirmação
        if st.button("Confirmar"):
            st.toast('Enviando alerta ')
            time.sleep(3)
            st.toast('Alerta cadastrado!', icon='🎉')
            time.sleep(.5)
            modal_alerta.close()

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

resultados = df[(df['bairro'] == bairro.replace(' ', '_')) & (df['quartos'] >= quartos) & (df['banheiros'] >= banheiros) & (df['banheiros'] >= banheiros) & (df['area'] >= area) & (df['preco'] <= preco)]
#drop duplicates with the link but keeping the one with the last date on the column 'last-seen'
resultados = resultados.drop_duplicates(subset=['link'], keep='last')

resultados_sem_data_scrape = resultados.drop(['Data_scrape', 'bairro', 'last_seen'], axis=1).reset_index(drop=True)
#instead of text, an mouse icon
resultados_sem_data_scrape['link'] = resultados_sem_data_scrape['link'].apply(lambda x: f'<a href="{x}">Imovel</a>')
#write the table with the clickable link fitting the screen
table_style = """
<style>
    table {{
        width: 100%;
        border-collapse: collapse;
    }}
    
</style>
"""



# Get the theme colors based on the selected theme


# Create the styled container and display the table
st.markdown(table_style.format(), unsafe_allow_html=True)

st.write(resultados_sem_data_scrape.to_html(escape=False, index=False), unsafe_allow_html=True)
