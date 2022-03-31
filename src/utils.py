"""Panopto2pod utilities."""
import configparser


def read_config():
    """Read config file settings."""
    config = configparser.ConfigParser()
    config.read("config/settings.ini")
    return config
