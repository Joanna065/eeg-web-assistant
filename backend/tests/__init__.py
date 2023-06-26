from unittest import TestCase

from eeg_web_assistant import settings


class BaseTestCase(TestCase):
    FIXTURE_DIR = settings.TestConfig.FIXTURE_DIR
