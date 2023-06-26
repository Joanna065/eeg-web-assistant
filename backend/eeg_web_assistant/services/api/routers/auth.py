from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from eeg_web_assistant import settings
from eeg_web_assistant.models.token import UserToken
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.services.logging import Logging
from eeg_web_assistant.utils.exceptions import AuthenticationError, ExceptionModel
from eeg_web_assistant.utils.security import authenticate_user, create_access_token

logger = Logging.get(__name__)

router = APIRouter()


@router.post('/token',
             response_model=UserToken,
             responses={401: {"model": ExceptionModel}})
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(Database)):
    logger.debug("Login for token by user with username {%s}", form_data.username)

    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise AuthenticationError()

    access_token_expires = timedelta(minutes=settings.SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(payload={'sub': user.username},
                                       expires_delta=access_token_expires)

    return {'username': form_data.username, 'access_token': access_token, 'token_type': 'bearer'}
