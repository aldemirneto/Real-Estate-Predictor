from config.ConfigManager import ConfigManager

class Logging:
    def __init__(self):
        self.config_manager = ConfigManager().get_config()
        self.log_file = self.config_manager['other_settings']['Log_file']

    def _write_to_log(self, message):
        with open(self.log_file, 'a') as f:
            f.write(message + '\n')

    def log(self, message):
        formatted_message = f"[INFO] {message}"
        self._write_to_log(formatted_message)

    def error(self, message):
        formatted_message = f"[ERROR] {message}"
        self._write_to_log(formatted_message)

    def log_email(self, email):
        formatted_message = f"[EMAIL] {email}"
        self._write_to_log(formatted_message)




