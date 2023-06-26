from celery import Celery
from celery.result import AsyncResult

from eeg_web_assistant import settings
from eeg_web_assistant.services import Service


class Worker(metaclass=Service):
    def __init__(self, config: settings.WorkerConfig):
        self.config = config

        self._app = Celery()
        self._app.config_from_object(self.config)

        from eeg_web_assistant.services.worker.tasks import classification
        self.classification = classification

    @property
    def app(self):
        return self._app

    def get_task(self, task_id: str):
        return AsyncResult(task_id, app=self._app)
