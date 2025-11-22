from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.order import OrderOut, OrderCreate
from app.services import order_service, auth_service

router = APIRouter()


@router.get('/', response_model=list[OrderOut])
def list_my_orders(db: Session = Depends(get_db), current_user=Depends(auth_service.get_current_user)):
  return order_service.list_orders(db, current_user.id)


@router.post('/', response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), current_user=Depends(auth_service.get_current_user)):
  return order_service.create_order(db, current_user.id, payload)


@router.get('/{order_id}', response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(auth_service.get_current_user)):
  return order_service.get_order(db, order_id, current_user.id)
