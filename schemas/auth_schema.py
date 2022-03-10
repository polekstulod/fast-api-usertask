from pydantic import BaseModel


class TokenData(BaseModel):
    author_id: str
    email: str

class AuthForm(BaseModel):
    email: str
    password: str
