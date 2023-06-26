from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from eeg_web_assistant import settings
from eeg_web_assistant.models.user import UserInDB
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.utils.exceptions import CredentialsError

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.SecurityConfig.TOKEN_URL)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Database) -> Optional[UserInDB]:
    user = db.users.find_one_by_username(username=username)

    if user and verify_password(password, user.get('password')):
        return UserInDB(**user)


def create_access_token(payload: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    expire = datetime.utcnow() + expires_delta

    to_encode = payload.copy()
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(claims=to_encode,
                             key=settings.SecurityConfig.SECRET_KEY,
                             algorithm=settings.SecurityConfig.ALGORITHM)

    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Database = Depends(Database)) -> UserInDB:
    try:
        payload = jwt.decode(token=token,
                             key=settings.SecurityConfig.SECRET_KEY,
                             algorithms=[settings.SecurityConfig.ALGORITHM])

        username: str = payload.get('sub')
        if username is None:
            raise CredentialsError()
    except JWTError:
        raise CredentialsError()

    user = db.users.find_one_by_username(username=username)
    if user is None:
        raise CredentialsError()

    return UserInDB(**user)
