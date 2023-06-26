from typing import Optional

from pydantic import BaseModel, EmailStr, constr


#  models to database insertion
class UserInDB(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str


# DTOs
class UserOut(BaseModel):
    first_name: constr(max_length=255)
    last_name: constr(max_length=255)
    email: EmailStr
    username: constr(max_length=50)

    class Config:
        extra = 'ignore'
        schema_extra = {
            'example': {
                'first_name': 'Adam',
                'last_name': 'Nowak',
                'email': 'nowak.adam@gmail.com',
                'username': 'a_nowak'
            }
        }


class CreateUser(BaseModel):
    first_name: constr(max_length=255)
    last_name: constr(max_length=255)
    email: EmailStr
    username: constr(max_length=50)
    password: constr(min_length=8, max_length=255)

    class Config:
        extra = 'forbid'
        schema_extra = {
            'example': {
                'first_name': 'Adam',
                'last_name': 'Nowak',
                'email': 'nowak.adam@gmail.com',
                'username': 'a_nowak',
                'password': 'adamnow987'
            }
        }


class UpdateUserPersonalInfo(BaseModel):
    first_name: Optional[constr(max_length=255)]
    last_name: Optional[constr(max_length=255)]
    email: Optional[EmailStr]

    class Config:
        extra = 'forbid'
        schema_extra = {
            'example': {
                'first_name': 'Adam',
                'last_name': 'Nowak',
                'email': 'nowak.adam@gmail.com'
            }
        }


class UpdateUserPassword(BaseModel):
    current_password: constr(min_length=8, max_length=255)
    new_password: constr(min_length=8, max_length=255)

    class Config:
        extra = 'forbid'
        schema_extra = {
            'example': {
                'current_password': 'adamnow987',
                'new_password': 'adamnow123'
            }
        }
