from pydantic import BaseModel


class PaymentRequest(BaseModel):
  items: list[dict[str, int]]


class PaymentResponse(BaseModel):
  orderId: int
  prepayParams: dict


class PaymentNotify(BaseModel):
  raw: str
