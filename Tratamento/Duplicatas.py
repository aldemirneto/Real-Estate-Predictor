import os
import pandas as pd

from typing import Optional, List
from pydantic import BaseModel, ValidationError
from datetime import date

# Define a Pydantic model for each row in the CSV file
class Imovel(BaseModel):
    preco: float
    area: float
    quartos: int
    vagas: str
    banheiros: str
    link: str
    Imobiliaria: str
    bairro: str
    Data_scrape: str
    last_seen: str = None



def validate_data(row: pd.Series) -> Optional[Imovel]:
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
    valid_df = valid_df.drop_duplicates(subset=['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria','bairro'])
    valid_df.loc[valid_df.duplicated(
        subset=['preco', 'area', 'quartos', 'vagas', 'banheiros', 'link', 'Imobiliaria', 'bairro'],
        keep=False), 'last_seen'] = date.today().strftime('%Y-%m-%d')
    valid_df = valid_df[valid_df['area'] > 2]
    valid_df.fillna({'vagas': 0, 'banheiros': 0, 'quartos': 0}, inplace=True)
    return valid_df

def run(filename: str) -> None:
    existing_data = pd.read_csv(filename, delimiter=';')
    valid_data = validate_and_filter_data(existing_data)
    valid_data.to_csv('output.csv', index=False, sep=';')
    os.replace('output.csv', filename)
