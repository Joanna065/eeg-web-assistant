import logging
import os
from logging.config import dictConfig

import yaml

from eeg_web_assistant import settings
from eeg_web_assistant.services import Service


class Logging(metaclass=Service):
    def __init__(self, config: settings.LoggingConfig):
        self.config = config
        self._logger = Logging.get(__name__)

        with self.config.PATH.open() as file:
            logging_config = yaml.full_load(file)
            dictConfig(logging_config)
            self._logger.debug("Loaded logging config %s: %s", self.config.PATH, logging_config)

        self._logger.debug("Environment variables: %s", dict(os.environ))
        self._logger.debug("Log directory: %s", settings.LoggingConfig.LOG_DIR.resolve())
        self._logger.info("Environment: %s", settings.ENVIRONMENT)

    @classmethod
    def get(cls, name: str):
        return logging.getLogger(name)
