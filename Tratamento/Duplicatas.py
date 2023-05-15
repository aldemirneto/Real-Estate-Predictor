import csv
import os

from pydantic import BaseModel
from datetime import datetime
import pandas as pd

# Define a Pydantic model for each row in the CSV file
class imovel(BaseModel):
    preco: float
    area: float
    quartos: int
    vagas: str
    banheiros: str
    link: str
    Imobiliaria:str
    bairro:str
    Data_scrape: str

def run(filename):
    # Read the existing CSV file and store it in a Pandas dataframe
    existing_data = pd.read_csv(filename, delimiter=';')

    # Iterate over the rows in the new data and validate the format
    valid_rows = []
    for _, row in existing_data.iterrows():
        # Parse the row into a Pydantic model
        try:
            imv = imovel(preco=float(row['preco']), area=float(row['area']), quartos=int(row['quartos']), bairro = row['bairro'] ,vagas=row['vagas'], banheiros=row['banheiros'], link=row['link'], Data_scrape=row['Data_scrape'], Imobiliaria = row['Imobiliaria'])
        except Exception as e:
            # If the row cannot be parsed, skip it
            print('Erro na conversão de tipos', e)
            continue

        # Add the validated row to the list
        valid_rows.append(imv)

    # Convert the list of validated rows to a Pandas dataframe
    new_data = pd.DataFrame([row.dict() for row in valid_rows])

    #update the existing data with the new data with the link column as the key
    merged_data = new_data.drop_duplicates(subset=['preco','area','quartos','vagas','banheiros','link','Imobiliaria','bairro'])

    merged_data = merged_data[['preco','area','quartos','vagas','banheiros','link','Imobiliaria','bairro','Data_scrape']]

    # Write the final data to a new CSV file
    merged_data.to_csv('output.csv', index=False, sep=';')

    # Overwrite the original CSV file with the modified version
    os.replace('output.csv', filename)

    
    