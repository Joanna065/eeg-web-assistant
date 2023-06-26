import unittest

from eeg_web_assistant import settings
from tests import BaseTestCase


@unittest.skipUnless(settings.TestConfig.INTEGRATION, reason='skip integration tests')
class IntegrationTestCase(BaseTestCase):
    pass
