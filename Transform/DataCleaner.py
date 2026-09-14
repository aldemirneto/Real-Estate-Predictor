import re
import unicodedata

from config.ConfigManager import ConfigManager


class DataCleaner:
    def __init__(self, rawData):
        config_manager = ConfigManager().get_config()
        self.blacklist = config_manager['BlackList']
        self.rawData = rawData

    @classmethod
    def replace_chars(cls, string):
        # Replace accented characters with their unaccented equivalents
        string = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode('utf-8')
        # Replace spaces with underscores
        if 'centro' in string.lower():
            string = 'Centro'
        if 'artemis' in string.lower():
            string = 'Artemis'
        string = re.sub(r',?\s*piracicaba[^,]*', '', string, flags=re.IGNORECASE)
        string = string.strip().replace(' ', '_')
        string = string.capitalize()
        return string

    def validate_data(self):
        #i have 4 nested lists, i need to flatten them
        data = [item for sublist in self.rawData for item in sublist]
        filtered_data = [item for item in data if item.get("cidade") == "São Paulo" or not any(term in self.replace_chars(item["bairro"]).lower() for term in self.blacklist)]
        #pass teh 'bairro' to the replace_chars method
        for item in filtered_data:
            item["bairro"] = (unicodedata.normalize("NFKD", item["bairro"]).encode("ascii", "ignore").decode().strip().replace(" ", "_").capitalize()
                             if item.get("cidade") == "São Paulo" else self.replace_chars(item["bairro"]))
            item.setdefault("cidade", "Piracicaba")
            item.setdefault("uf", "SP")
        return filtered_data

