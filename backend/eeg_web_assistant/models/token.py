from pydantic.main import BaseModel


class UserToken(BaseModel):
    username: str
    access_token: str
    token_type: str
