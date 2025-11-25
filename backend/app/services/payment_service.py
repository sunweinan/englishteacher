import hashlib
import secrets
import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.integration import IntegrationConfig
from app.models.payment import Payment
from app.services.order_service import create_order
from app.schemas.order import OrderCreate
from app.schemas.payment import PaymentRequest


def _load_wechat_integration(db: Session) -> dict:
  record = (
    db.query(IntegrationConfig)
    .filter(IntegrationConfig.provider == 'wechat_pay')
    .first()
  )
  if not record or not record.is_active or not isinstance(record.config, dict):
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail='微信支付未配置或未激活，请在后台完善集成信息后重试'
    )
  return record.config


def generate_wechat_signature(*, app_id: str, api_key: str, package: str) -> dict:
  timestamp = str(int(time.time()))
  nonce_str = secrets.token_hex(8)
  base_string = f"{app_id}:{package}:{nonce_str}:{timestamp}:{api_key}"
  pay_sign = hashlib.sha256(base_string.encode()).hexdigest()
  return {
    'timeStamp': timestamp,
    'nonceStr': nonce_str,
    'package': package,
    'signType': 'HMAC-SHA256',
    'paySign': pay_sign
  }


def build_js_config(*, url: str, app_id: str, api_key: str) -> dict:
  timestamp = str(int(time.time()))
  nonce_str = secrets.token_hex(8)
  signature_payload = f"{app_id}:{url}:{nonce_str}:{timestamp}:{api_key}"
  signature = hashlib.sha256(signature_payload.encode()).hexdigest()
  return {
    'appId': app_id,
    'timestamp': timestamp,
    'nonceStr': nonce_str,
    'signature': signature
  }


def create_wechat_payment(db: Session, user_id: int, payload: PaymentRequest):
  config = _load_wechat_integration(db)
  app_id = str(config.get('appId') or '')
  api_key = str(config.get('apiKey') or '')
  if not app_id or not api_key:
    raise HTTPException(status_code=503, detail='微信支付配置缺失，无法创建订单')

  order = create_order(db, user_id, OrderCreate(items=payload.items))
  payment = Payment(order_id=order.id, provider='wechat', status='pending')
  db.add(payment)
  db.commit()
  db.refresh(payment)
  package = f"prepay_id={payment.id}"
  prepay_params = generate_wechat_signature(app_id=app_id, api_key=api_key, package=package)
  return {'orderId': order.id, 'prepayParams': prepay_params}


def load_wechat_js_config(db: Session, *, url: str) -> dict:
  config = _load_wechat_integration(db)
  app_id = str(config.get('appId') or '')
  api_key = str(config.get('apiKey') or '')
  if not app_id or not api_key:
    raise HTTPException(status_code=503, detail='微信支付配置缺失，无法生成前端参数')
  return build_js_config(url=url, app_id=app_id, api_key=api_key)


def handle_notify(db: Session, raw: str):
  payment = db.query(Payment).first()
  if not payment:
    raise HTTPException(status_code=404, detail='Payment not found')
  payment.raw_notify = raw
  payment.status = 'paid'
  db.commit()
  return payment
