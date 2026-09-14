import pandas as pd
from config.ConfigManager import ConfigManager
from sqlalchemy import create_engine, inspect, text
import os
from sqlalchemy.engine import URL


class DataStorage:
    def __init__(self):
        config = ConfigManager().get_config()
        self.engine = None
        self.connection = None
        self.bairros = None
        self.status = None
        self.imobiliarias = None

    def connect_to_database(self):
        host     = os.environ["DB_HOST"]
        port     = os.environ.get("DB_PORT", "5432")
        user     = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        name     = os.environ["DB_NAME"]
        string_con = URL.create("postgresql+psycopg2", username=user, password=password, host=host, port=int(port), database=name)
        e = create_engine(string_con)
        self.connection = e.connect()
        self.engine = e
        return 1

    def get_bairro_id(self, bairro):

        if self.bairros is None:
            self.bairros = pd.read_sql(text('select bairroid, bairrodesc from bairro'), con=self.connection)

        # if the bairro is not on the dataframe, i will insert it on the database and return the id
        if bairro not in self.bairros['bairrodesc'].values:
            query = text("INSERT INTO bairro (bairrodesc) VALUES (:value) ON CONFLICT DO NOTHING")
            self.connection.execute(query, {"value": bairro})
            self.bairros = pd.read_sql(sql=text("SELECT bairroid, bairrodesc FROM bairro"), con=self.connection)

        return self.bairros[self.bairros['bairrodesc'] == bairro]['bairroid'].values[0]

    def get_status_id(self, status):
        if self.status is None:
            self.status = pd.read_sql(text('SELECT statusid, statusdesc FROM Status'), con=self.connection)

        if status not in self.status['statusdesc'].values:
            query = text("INSERT INTO status (statusdesc) VALUES (:value) ON CONFLICT DO NOTHING")
            self.connection.execute(query, {"value": status})
            self.status = pd.read_sql(text('SELECT statusid, statusdesc FROM status'), con=self.connection)

        return self.status[self.status['statusdesc'] == status]['statusid'].values[0]

    def get_imobiliaria_id(self, imobiliaria):
        if self.imobiliarias is None:
            self.imobiliarias = pd.read_sql(text('SELECT imobiliariaid, imobiliariadesc FROM imobiliaria'), con=self.connection)

        if imobiliaria not in self.imobiliarias['imobiliariadesc'].values:
            query = text("INSERT INTO imobiliaria (imobiliariadesc) VALUES (:value) ON CONFLICT DO NOTHING")
            self.connection.execute(query, {"value": imobiliaria})
            self.imobiliarias = pd.read_sql(text('SELECT imobiliariaid, imobiliariadesc FROM imobiliaria'), con=self.connection)

        return self.imobiliarias[self.imobiliarias['imobiliariadesc'] == imobiliaria]['imobiliariaid'].values[0]

    def save_data(self, df):
        if df.empty:
            raise ValueError("Extração vazia; banco preservado")
        if self.engine is None:
            self.connect_to_database()
        df = df.copy().dropna(subset=['bairro', 'Imobiliaria', 'Status', 'link'])
        if df.empty:
            raise ValueError("Nenhum imóvel válido; banco preservado")
        try:
            columns = {c['name'] for c in inspect(self.connection).get_columns('temp_imovel', schema='public')}
            cities_enabled = 'cidade' in columns
            if not cities_enabled and (df.get('cidade', pd.Series('Piracicaba', index=df.index)) != 'Piracicaba').any():
                raise RuntimeError("Execute sql/catalog_cities.sql antes de carregar outras cidades")
            city_columns = ', cidade, uf' if cities_enabled else ''
            city_update = ', cidade=EXCLUDED.cidade, uf=EXCLUDED.uf' if cities_enabled else ''
            df['cidade'] = df.get('cidade', 'Piracicaba')
            df['uf'] = df.get('uf', 'SP')
            df['bairro'] = df['bairro'].apply(self.get_bairro_id)
            df['Imobiliaria'] = df['Imobiliaria'].apply(self.get_imobiliaria_id)
            df['Status'] = df['Status'].apply(self.get_status_id)
            df['Data_scrape'] = pd.Timestamp.today().date()
            df['last_seen'] = pd.Timestamp.today().date()
            df = df.drop_duplicates(subset=['link'])
            if not cities_enabled:
                df = df.drop(columns=['cidade', 'uf'])
            self.connection.execute(text('TRUNCATE TABLE temp_imovel'))
            df.to_sql('temp_imovel', con=self.connection, if_exists='append', index=False, schema='public')
            self.connection.execute(text(f"""
                INSERT INTO imovel (preco, area, quartos, vagas, banheiros, bairro, status,
                                    data_scrape, last_seen, link, tipo, imobiliaria{city_columns})
                SELECT preco, area, quartos, vagas, banheiros, bairro, "Status",
                       "Data_scrape", last_seen, link, tipo, "Imobiliaria"{city_columns}
                FROM temp_imovel WHERE link IS NOT NULL
                ON CONFLICT (link) DO UPDATE SET
                    preco=EXCLUDED.preco, area=EXCLUDED.area, quartos=EXCLUDED.quartos,
                    vagas=EXCLUDED.vagas, banheiros=EXCLUDED.banheiros, bairro=EXCLUDED.bairro,
                    status=EXCLUDED.status, last_seen=EXCLUDED.last_seen, tipo=EXCLUDED.tipo,
                    imobiliaria=EXCLUDED.imobiliaria{city_update}
            """))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            self.connection.close()
            self.bairros = self.status = self.imobiliarias = None
        return 'Salvo Com Sucesso!'
