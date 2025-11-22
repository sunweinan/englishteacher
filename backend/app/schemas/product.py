from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  stock: int

  class Config:
    orm_mode = True


class ProductCreate(ProductBase):
  pass


class ProductOut(ProductBase):
  id: int
