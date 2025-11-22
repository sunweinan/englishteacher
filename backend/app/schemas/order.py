from typing import List
from pydantic import BaseModel
from app.schemas.product import ProductOut


class OrderItemBase(BaseModel):
  product_id: int
  quantity: int


class OrderItemOut(OrderItemBase):
  price: float
  product: ProductOut | None = None

  class Config:
    orm_mode = True


class OrderCreate(BaseModel):
  items: List[OrderItemBase]


class OrderOut(BaseModel):
  id: int
  status: str
  total_amount: float
  items: List[OrderItemOut] = []

  class Config:
    orm_mode = True
