"""
Copyright (C) 2024 Jath Palasubramaniam
Licensed under the Affero General Public License version 3
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from kubera_server.logging import get_logger

logger = get_logger()

class Settings(BaseSettings):
    """
    Configuration variables
    """

    service_name: str = "kubera"
    service_version: str = "1.0"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    """
    Return a cached copy of the settings object
    """
    return Settings()
