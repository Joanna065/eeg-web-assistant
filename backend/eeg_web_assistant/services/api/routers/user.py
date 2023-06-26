from fastapi import APIRouter, Depends, status

from eeg_web_assistant.models.user import (CreateUser, UpdateUserPassword, UpdateUserPersonalInfo,
                                           UserInDB, UserOut)
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.services.logging import Logging
from eeg_web_assistant.utils.exceptions import (DuplicatedEmailError, DuplicatedUsernameError,
                                                ExceptionModel, NotValidPassword, UserNotFoundError)
from eeg_web_assistant.utils.security import get_current_user, get_password_hash, verify_password

logger = Logging.get(__name__)

router = APIRouter()


@router.post('',
             status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel}})
def create_user(new_user: CreateUser, db: Database = Depends(Database)):
    logger.debug("Create user called")

    user_same_username = db.users.find_one_by_username(username=new_user.username)
    if user_same_username:
        raise DuplicatedUsernameError()

    user_same_email = db.users.find_one_by_email(email=new_user.email)
    if user_same_email:
        raise DuplicatedEmailError()

    new_user.password = get_password_hash(password=new_user.password)
    inserted_id = db.users.insert_one(new_user.dict(exclude_unset=True))

    return inserted_id


@router.get('',
            response_model=UserOut,
            responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel}})
def retrieve_current_user(user: UserInDB = Depends(get_current_user)):
    logger.debug("Get current user data called by user {%s}", user.username)

    return user


@router.patch('/password',
              responses={status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
                         status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel},
                         status.HTTP_404_NOT_FOUND: {"model": ExceptionModel}})
def update_user_password(updated_user: UpdateUserPassword,
                         user: UserInDB = Depends(get_current_user),
                         db: Database = Depends(Database)):
    logger.debug("Update password called by user {%s}", user.username)

    if not verify_password(plain_password=updated_user.current_password,
                           hashed_password=user.password):
        raise NotValidPassword()

    new_password = get_password_hash(password=updated_user.new_password)

    updated_user = db.users.find_one_and_update(username=user.username,
                                                update_data={'password': new_password})

    if not updated_user:
        raise UserNotFoundError()

    return str(updated_user.get('_id'))


@router.patch('/personal_info',
              responses={status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
                         status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel},
                         status.HTTP_404_NOT_FOUND: {"model": ExceptionModel}})
def update_user_personal_info(updated_user: UpdateUserPersonalInfo,
                              user: UserInDB = Depends(get_current_user),
                              db: Database = Depends(Database)):
    logger.debug("Update personal info called by user {%s}", user.username)

    if updated_user.dict(exclude_unset=True, exclude_none=True):
        if updated_user.email:
            user_same_email = db.users.find_one_by_email(email=updated_user.email)
            if user_same_email:
                raise DuplicatedEmailError()

        updated_user = db.users.find_one_and_update(
            username=user.username,
            update_data=updated_user.dict(exclude_unset=True, exclude_none=True))

        if not updated_user:
            raise UserNotFoundError()

        return str(updated_user.get('_id'))


@router.delete('',
               responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel},
                          status.HTTP_404_NOT_FOUND: {"model": ExceptionModel}})
def delete_user(user: UserInDB = Depends(get_current_user), db: Database = Depends(Database)):
    logger.debug("Delete user called by user {%s}", user.username)

    deleted_user = db.users.find_one_and_delete(username=user.username)
    if not deleted_user:
        raise UserNotFoundError()

    raw_to_delete = [rec['raw_id'] for rec in
                     db.recordings_data.find_many_by_username_return_raw_ids(
                         username=user.username)]

    for raw_id in raw_to_delete:
        db.recordings_raw.delete(file_id=raw_id)

    db.recordings_data.find_many_and_delete(username=user.username)

    return str(deleted_user.get('_id'))
