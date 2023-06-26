from eeg_web_assistant import settings
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.services.logging import Logging
from eeg_web_assistant.services.worker import Worker

logging = Logging.create(config=settings.LoggingConfig())
worker = Worker.create(config=settings.WorkerConfig())
database = Database.create(config=settings.DatabaseConfig())

app = worker.app

if __name__ == '__main__':
    from celery.bin.worker import worker

    worker(app=app).run()
