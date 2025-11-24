from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.services import payment_service, auth_service

router = APIRouter()


@router.post('/wechat', response_model=PaymentResponse)
def wechat_pay(payload: PaymentRequest, db: Session = Depends(get_db), current_user=Depends(auth_service.get_current_user)):
  return payment_service.create_wechat_payment(db, current_user.id, payload)


@router.post('/wechat/notify')
async def wechat_notify(request: Request, db: Session = Depends(get_db)):
  raw = await request.body()
  payment_service.handle_notify(db, raw.decode())
  return {'status': 'success'}


@router.get('/wechat/config')
def wechat_config(url: str):
  return payment_service.build_wechat_js_config(url)
