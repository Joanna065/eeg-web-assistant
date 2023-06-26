from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from eeg_web_assistant import __version__, settings
from eeg_web_assistant.services import Service
from eeg_web_assistant.services.api.routers import classification


class API(metaclass=Service):
    def __init__(self, config: settings.APIConfig):
        self.config = config

        self._app = FastAPI(
            root_path=self.config.ROOT_PATH,
            title=self.config.TITLE,
            description=self.config.DESCRIPTION,
            version=__version__,
        )

        origins = ['http://localhost:8080']

        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

        from eeg_web_assistant.services.api.routers import auth, recording, user

        self._app.include_router(user.router, prefix='/user', tags=['user'])
        self._app.include_router(auth.router, prefix='/auth', tags=['auth'])
        self._app.include_router(recording.router, prefix='/recording', tags=['recording'])
        self._app.include_router(classification.router, prefix='/classification',
                                 tags=['classification'])

    @property
    def app(self):
        return self._app
