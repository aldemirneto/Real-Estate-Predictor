import os

import numpy
import pandas as pd

from typing import Optional, List

from numpy import NaN
from pydantic import BaseModel, ValidationError
from datetime import date

# Define a Pydantic model for each row in the CSV file
class Imovel(BaseModel):
    preco: float
    area: float
    quartos: float | int
    vagas: float | int
    banheiros: float | int
    link: str=None
    Imobiliaria: str=None
    bairro: str=None
    Data_scrape: str=None
    last_seen: Optional[str]=None



def validate_data(row: pd.Series) -> Optional[Imovel]:
    row = row.where(pd.notnull(row), None)
    try:
        return Imovel(**row.to_dict())
    except ValidationError as e:
        print(f"{row}")
        print('Erro na conversão de tipos', e)
        return None

def validate_and_filter_data(df: pd.DataFrame) -> pd.DataFrame:
    valid_rows = [validate_data(row) for _, row in df.iterrows()]
    valid_rows = [row for row in valid_rows if row is not None]  # filter out None values
    valid_df = pd.DataFrame([row.dict() for row in valid_rows])
    merged_data = valid_df.copy()
    merged_data.loc[merged_data.duplicated(
        subset=['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro'],
        keep=False), 'last_seen'] = date.today().strftime('%Y-%m-%d')
    # update the existing data with the new data with the link column as the key

    merged_data = merged_data.drop_duplicates(
        subset=['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro'])


    merged_data = merged_data[merged_data['area'] > 2]
    merged_data.fillna({'vagas': 0, 'banheiros': 0, 'quartos': 0}, inplace=True)
    return merged_data

def run(filename: str) -> None:
    existing_data = pd.read_csv(filename, delimiter=';')
    valid_data = validate_and_filter_data(existing_data)
    valid_data.to_csv('output.csv', index=False, sep=';')
    os.replace('output.csv', filename)
