from eeg_web_assistant import settings
from eeg_web_assistant.services.api import API
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.services.logging import Logging
from eeg_web_assistant.services.worker import Worker

logging = Logging.create(config=settings.LoggingConfig())
worker = Worker.create(config=settings.WorkerConfig())
database = Database.create(config=settings.DatabaseConfig())
api = API.create(config=settings.APIConfig())

app = api.app

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, log_config=None)
