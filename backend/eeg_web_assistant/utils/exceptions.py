from fastapi import HTTPException, status
from pydantic import BaseModel

from eeg_web_assistant import settings


class ExceptionModel(BaseModel):
    detail: str


class DuplicatedEmailError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Email is already occupied")


class DuplicatedUsernameError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Username is already occupied")


class NotValidPassword(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Current password is not valid")


class EdfExtensionError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Not an .edf file")


class EdfReadError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Could not read the file content")


class EdfDurationExceededError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Edf file duration above {settings.EdfFileConfig.MAX_DURATION_MINUTES} minutes"
        )


class PlotFragmentNrExceededError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Requested plot nr exceeds available fragments amount")


class NonExistingClassificationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="Classification report does not exist")


class AuthenticationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Incorrect username or password",
                         headers={"WWW-Authenticate": "Bearer"})


class CredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Unable to validate credentials",
                         headers={"WWW-Authenticate": "Bearer"})


class RecordingForbiddenAccessError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail="Forbidden access to this recording")


class UserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class RecordingNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")
