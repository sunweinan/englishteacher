import secrets
import time
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.services.order_service import create_order
from app.schemas.payment import PaymentRequest
from app.schemas.order import OrderCreate


def generate_wechat_signature() -> dict:
  return {
    'timeStamp': str(int(time.time())),
    'nonceStr': secrets.token_hex(8),
    'package': 'prepay_id=mock',
    'signType': 'RSA',
    'paySign': secrets.token_hex(16)
  }


def create_wechat_payment(db: Session, user_id: int, payload: PaymentRequest):
  order = create_order(db, user_id, OrderCreate(items=payload.items))
  payment = Payment(order_id=order.id, provider='wechat', status='pending')
  db.add(payment)
  db.commit()
  db.refresh(payment)
  prepay_params = generate_wechat_signature()
  return {'orderId': order.id, 'prepayParams': prepay_params}


def handle_notify(db: Session, raw: str):
  payment = db.query(Payment).first()
  if not payment:
    raise HTTPException(status_code=404, detail='Payment not found')
  payment.raw_notify = raw
  payment.status = 'paid'
  db.commit()
  return payment
