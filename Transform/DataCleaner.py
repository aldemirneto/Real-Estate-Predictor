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
        string = string.replace(', piracicaba', '').replace(', PIRACICABA', '')
        string = string.strip().replace(' ', '_')
        string = string.capitalize()
        return string

    def validate_data(self):
        #i have 4 nested lists, i need to flatten them
        data = [item for sublist in self.rawData for item in sublist]
        filtered_data = [item for item in data if not any(term in self.replace_chars(item["bairro"]).lower() for term in self.blacklist)]
        #pass teh 'bairro' to the replace_chars method
        for item in filtered_data:
            item["bairro"] = self.replace_chars(item["bairro"])
        return filtered_data

