from pydantic import BaseModel


class Token(BaseModel):
  access_token: str
  token_type: str = 'bearer'
  is_default_admin: bool | None = None


class LoginRequest(BaseModel):
  username: str
  password: str
