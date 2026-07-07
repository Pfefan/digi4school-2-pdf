import os
from configparser import RawConfigParser


class ConfigHandler:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file

    def check_config(self) -> bool:
        config = RawConfigParser()
        if not os.path.isfile(self.config_file):
            config['DEFAULT'] = {
                'email': 'email',
                'password': 'password',
            }
            with open(self.config_file, 'w+', encoding="utf-8") as configfile:
                config.write(configfile)
            return False
        else:
            config.read(self.config_file)
            try:
                email = config['DEFAULT']['email']
                password = config['DEFAULT']['password']
            except KeyError:
                config['DEFAULT'] = {
                    'email': 'email',
                    'password': 'password',
                }
                with open(self.config_file, 'w+', encoding="utf-8") as configfile:
                    config.write(configfile)
                return False

        if email == "email" or password == "password":
            return False
        else:
            return True

    def get_config(self):
        config = RawConfigParser()
        config.read(self.config_file)
        return config['DEFAULT']

    def write_config(self, email, password):
        config = RawConfigParser()
        config['DEFAULT'] = {
            'email': email,
            'password': password,
        }
        with open(self.config_file, 'w+', encoding="utf-8") as configfile:
            config.write(configfile)
