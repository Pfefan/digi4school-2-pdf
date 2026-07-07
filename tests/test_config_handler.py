import os
import pytest
import tempfile
from configparser import RawConfigParser
from src.handlers.config_handler import ConfigHandler

class TestConfigHandler:
    @pytest.fixture
    def config_handler(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.close()
            yield ConfigHandler(config_file=temp.name)
            os.remove(temp.name)

    def test_check_config_no_file(self, config_handler):
        result = config_handler.check_config()

        assert result is False
        assert os.path.isfile(config_handler.config_file)
        config = RawConfigParser()
        config.read(config_handler.config_file)
        assert config['DEFAULT']['email'] == 'email'
        assert config['DEFAULT']['password'] == 'password'

    def test_check_config_no_values(self, config_handler):
        config = RawConfigParser()
        config['DEFAULT'] = {
            'email': 'email',
            'password': 'password',
        }
        with open(config_handler.config_file, 'w+', encoding="utf-8") as configfile:
            config.write(configfile)

        result = config_handler.check_config()

        assert result is False

    def test_check_config_values_set(self, config_handler):
        config = RawConfigParser()
        config['DEFAULT'] = {
            'email': 'test@example.com',
            'password': 'test123',
        }
        with open(config_handler.config_file, 'w+', encoding="utf-8") as configfile:
            config.write(configfile)

        result = config_handler.check_config()

        assert result is True

    def test_get_config(self, config_handler):
        config = RawConfigParser()
        config['DEFAULT'] = {
            'email': 'test@example.com',
            'password': 'test123',
        }
        with open(config_handler.config_file, 'w+', encoding="utf-8") as configfile:
            config.write(configfile)

        result = config_handler.get_config()

        assert result['email'] == 'test@example.com'
        assert result['password'] == 'test123'