import pandas as pd
from Alert.Alerta import Alerta
from Transform.DataCleaner import DataCleaner
from config.ConfigManager import ConfigManager
from Log.Logging import Logging
import importlib
from connection.DataStorage import DataStorage


class MainOrchestrator:
    def __init__(self):
        self.config = ConfigManager().get_config()
        self.websites = []
        self.log = Logging()

    def get_websites(self):
        for website in self.config['websites']:
            if self.config['websites'][website]['Ativo']:
                self.websites.append(website)


    def Extract(self):
        data = []
        if self.websites == []:
            self.get_websites()

        for website in self.websites:
            try:
                Scraper = website + "Scraper"
                module_name = f"Extract.{Scraper}"
                module = importlib.import_module(module_name)
                class_ = getattr(module, Scraper)
                instance = class_()
                dt = instance.scrape()
                data.append(dt)
                self.log.log(f"{len(dt)}Imoveis extraidos do site {website}")
            except Exception as e:
                self.log.log(f"Erro ao extrair do site {website}: {e}")
        self.log.log(f"{len(data)}Imoveis extraídos")
        return self.Transform(data)

    def Transform(self, data):
        Cleaner = DataCleaner(data)
        filtered_data = Cleaner.validate_data()
        self.log.log(f"{len(filtered_data)}Imoveis corretos")
        return self.Load(filtered_data)


    def Load(self, data):
        #transform this list of dicts into a dataframe
        #then, load it into the database
        dataf = pd.DataFrame(data)
        Loader = DataStorage()
        Loader.connect_to_database()
        Loader.save_data(dataf)
        self.log.log(f"{len(dataf)}Imoveis carregados")



