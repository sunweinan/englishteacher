from pydantic import BaseModel


class UserBase(BaseModel):
  username: str
  role: str

  class Config:
    orm_mode = True


class UserCreate(BaseModel):
  username: str
  password: str
  role: str = 'user'


class UserOut(UserBase):
  id: int
