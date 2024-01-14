import pandas as pd
from config.ConfigManager import ConfigManager
from sqlalchemy import create_engine, event, engine, text
import os
from sqlalchemy.engine import url


class DataStorage:
    def __init__(self):
        config = ConfigManager().get_config()
        self.engine = None
        self.connection = None
        self.bairros = None
        self.status = None
        self.imobiliarias = None

    def connect_to_database(self):
        string_con = url.URL(
            'postgresql+psycopg2',  # Using psycopg2 as the driver for connecting to PostgreSQL
            username=os.environ['db_username'],
            password=os.environ['db_password'],
            host=os.environ['db_host'],
            port=os.environ['db_port'],
            database=os.environ['db_database_name'],
            query={
                'sslmode': 'require'
            }
        )

        e = create_engine(string_con)
        self.connection = e.connect()
        self.engine = e
        return 1

    def get_bairro_id(self, bairro):

        if self.bairros is None:
            self.bairros = pd.read_sql(text('select bairroid, bairrodesc from bairro'), con=self.connection)

        # if the bairro is not on the dataframe, i will insert it on the database and return the id
        if bairro not in self.bairros['bairrodesc'].values:
            query = text(f"INSERT INTO bairro (bairrodesc) VALUES ('{bairro}')")
            self.connection.execute(query)
            self.bairros = pd.read_sql(sql=text("SELECT bairroid, bairrodesc FROM bairro"), con=self.connection)

        return self.bairros[self.bairros['bairrodesc'] == bairro]['bairroid'].values[0]

    def get_status_id(self, status):
        if self.status is None:
            self.status = pd.read_sql(text('SELECT statusid, statusdesc FROM Status'), con=self.connection)

        if status not in self.status['statusdesc'].values:
            query = text(f"INSERT INTO status (statusdesc) VALUES ('{status}')")
            self.connection.execute(query)
            self.status = pd.read_sql(text('SELECT statusid, statusdesc FROM status'), con=self.connection)

        return self.status[self.status['statusdesc'] == status]['statusid'].values[0]

    def get_imobiliaria_id(self, imobiliaria):
        if self.imobiliarias is None:
            self.imobiliarias = pd.read_sql(text('SELECT imobiliariaid, imobiliariadesc FROM imobiliaria'), con=self.connection)

        if imobiliaria not in self.imobiliarias['imobiliariadesc'].values:
            query = text(f"INSERT INTO Imobiliaria (imobiliariadesc) VALUES ('{imobiliaria}')")
            self.connection.execute(query)
            self.imobiliarias = pd.read_sql(text('SELECT imobiliariaid, imobiliariadesc FROM imobiliaria'), con=self.connection)

        return self.imobiliarias[self.imobiliarias['imobiliariadesc'] == imobiliaria]['imobiliariaid'].values[0]

    def save_data(self, df):
        if self.engine is None:
            self.connect_to_database()
        #take ' from bairro column

        df['bairro'] = df['bairro'].apply(lambda x: x.replace("'", ""))

        df['bairro'] = df['bairro'].apply(lambda x: self.get_bairro_id(x))
        # capitalize imobiliaria and change ' ' for '_'
        df['Imobiliaria'] = df['Imobiliaria'].apply(lambda x: x.capitalize().replace(' ', '_'))
        df['Imobiliaria'] = df['Imobiliaria'].apply(lambda x: self.get_imobiliaria_id(x))
        df['Status'] = df['Status'].apply(lambda x: self.get_status_id(x))
        df['Data_scrape'] = pd.to_datetime('today').strftime('%Y-%m-%d')
        df['last_seen'] = pd.to_datetime('today').strftime('%Y-%m-%d')
        df.to_sql('temp_imovel', con=self.engine, if_exists='replace', index=False,
                  schema='public')  # Changed schema to 'public'
        self.connection.execute(text('commit'))
        self.connection.execute(text("""
        INSERT INTO
          imovel (
            bairroid,
            imobiliariaid,
            statusid,
            preco,
            area,
            quartos,
            vagas,
            banheiros,
            link,
            Data_scrape,
            last_seen,
            tipo
          )
        SELECT distinct
          temp_imovel.bairro,
          temp_imovel."Imobiliaria",
          temp_imovel."Status",
          CASE WHEN preco ~ E'^\\d+(\\.\\d+)?$' THEN CAST(preco AS FLOAT) ELSE 0 END AS preco,
          CASE WHEN area ~ E'^\\d+(\\.\\d+)?$' THEN CAST(area AS FLOAT) ELSE 0 END AS area,
          CASE WHEN quartos ~ E'^\\d+$' THEN CAST(quartos AS INT) ELSE 0 END AS quartos,
          CASE WHEN vagas ~ E'^\\d+$' THEN CAST(vagas AS INT) ELSE 0 END AS vagas,
          CASE WHEN banheiros ~ E'^\\d+$' THEN CAST(banheiros AS INT) ELSE 0 END AS banheiros,
          link,
          CAST(temp_imovel."Data_scrape" AS DATE) AS "Data_scrape",
          CURRENT_DATE,
          temp_imovel.tipo
        FROM
          temp_imovel 
        WHERE
          preco IS NOT NULL   
          ON CONFLICT ON CONSTRAINT unique_imovel_constraint
        DO
        UPDATE
        SET
          tipo = excluded.tipo,
          last_seen = CURRENT_DATE;

        """))

        self.connection.execute(text('commit'))
        self.connection.close()
        return 'Salvo Com Sucesso!'
