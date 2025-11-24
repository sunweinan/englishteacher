from pydantic import BaseModel


class UserBase(BaseModel):
  username: str
  role: str
  phone: str
  membership_level: str
  membership_expires_at: str | None = None

  class Config:
    orm_mode = True


class UserCreate(BaseModel):
  username: str
  password: str
  phone: str | None = None
  role: str = 'user'
  membership_level: str = 'free'
  membership_expires_at: str | None = None


class UserOut(UserBase):
  id: int
