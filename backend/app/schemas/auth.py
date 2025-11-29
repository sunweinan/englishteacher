from pydantic import BaseModel


class Token(BaseModel):
  access_token: str
  token_type: str = 'bearer'
  is_default_admin: bool | None = None


class LoginRequest(BaseModel):
  username: str
  password: str


class SendCodeRequest(BaseModel):
  phone: str


class PhoneLoginRequest(BaseModel):
  phone: str
  code: str


class LoginResponse(Token):
  user: 'UserOut'
  newly_registered: bool = False


from app.schemas.user import UserOut  # noqa: E402  pylint: disable=wrong-import-position

LoginResponse.update_forward_refs()
