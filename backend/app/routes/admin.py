from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserOut
from app.schemas.product import ProductOut, ProductCreate
from app.schemas.order import OrderOut
from app.services import auth_service, product_service, order_service
from app.models.user import User

router = APIRouter(dependencies=[Depends(auth_service.get_current_admin)])


@router.get('/users', response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
  return db.query(User).all()


@router.get('/products', response_model=list[ProductOut])
def admin_products(db: Session = Depends(get_db)):
  return product_service.list_products(db)


@router.post('/products', response_model=ProductOut)
def admin_create_product(payload: ProductCreate, db: Session = Depends(get_db)):
  return product_service.create_product(db, payload)


@router.put('/products/{product_id}', response_model=ProductOut)
def admin_update_product(product_id: int, payload: ProductCreate, db: Session = Depends(get_db)):
  return product_service.update_product(db, product_id, payload)


@router.delete('/products/{product_id}')
def admin_delete_product(product_id: int, db: Session = Depends(get_db)):
  product_service.delete_product(db, product_id)
  return {'status': 'deleted'}


@router.get('/orders', response_model=list[OrderOut])
def admin_orders(db: Session = Depends(get_db)):
  return order_service.list_orders(db)


@router.get('/orders/{order_id}', response_model=OrderOut)
def admin_order_detail(order_id: int, db: Session = Depends(get_db)):
  return order_service.get_order(db, order_id)
