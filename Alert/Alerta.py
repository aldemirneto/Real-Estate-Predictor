import datetime
import json

import pandas as pd
from sqlalchemy import text

from Alert.Email import EmailSender
from Log.Logging import Logging
from config.ConfigManager import ConfigManager
from connection.DataStorage import DataStorage


class Alerta:
    def __init__(self):
        self.config = ConfigManager().get_config()
        self.log = Logging()
        self.data = None

        self.connection = DataStorage()
    # here we get all the alerts from the database
    # and send the

    def _get_data(self):
        self.connection.connect_to_database()
        self.data = pd.read_sql(text('SELECT * FROM real_estate_data_mt'), con=self.connection.connection)


    def _get_alertas(self):
        return pd.read_sql(text('SELECT * FROM alerta'), con=self.connection.connection)


    def send_imoveis(self):
        #get all the alerts
        self._get_data()
        alertas = self._get_alertas()


        #for each row in the alertas dataframe
        for index, row in alertas.iterrows():
            #this is the json that contains the alerta
            alerta_json = row['criterios']
            #convert the column 'quarto' to int
            self.data['quartos'] = self.data['quartos'].astype(int) if 'quartos' in self.data.columns else 0
            self.data['banheiros'] = self.data['banheiros'].astype(int) if 'banheiros' in self.data.columns else 0
            self.data['vagas'] = self.data['vagas'].astype(int) if 'vagas' in self.data.columns else 0
            self.data['area'] = self.data['area'].astype(float) if 'area' in self.data.columns else 0
            self.data['preco'] = self.data['preco'].astype(float) if 'preco' in self.data.columns else 0

            alerta_json['quartos'] = alerta_json['quartos'] if 'quartos' in alerta_json else 0
            alerta_json['banheiros'] = alerta_json['banheiros'] if 'banheiros' in alerta_json else 0
            alerta_json['vagas'] = alerta_json['vagas'] if 'vagas' in alerta_json else 0
            alerta_json['area'] = alerta_json['area'] if 'area' in alerta_json else 0
            alerta_json['preco'] = alerta_json['preco'] if 'preco' in alerta_json else 0

            imoveis = self.data[(self.data['quartos'] >= alerta_json['quartos']) & (self.data['banheiros'] >= alerta_json['banheiros']) & (self.data['vagas'] >= alerta_json['vagas']) & (self.data['area'] >= alerta_json['area']) & (self.data['preco'] <= alerta_json['preco'] if  alerta_json['preco'] != 0 else self.data['preco'] >= 0)]
            self.send_email(imoveis, row['usuario'])



    def send_email(self, imoveis, email):
        #create the email
        email = EmailSender(imoveis, email)
        #send the email
        email.envio()
        #log the email
        self.log.log_email(email)

