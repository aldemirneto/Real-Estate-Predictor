import json

class ConfigManager:
    def __init__(self):
        self.config_file = 'config\config.json'
        self.config = None

    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        return self.config

    def get_config(self):
        if self.config is None:
            self.load_config()
        return self.config


