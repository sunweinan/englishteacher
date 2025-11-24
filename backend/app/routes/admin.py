from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserOut
from app.schemas.admin import DatabaseTestRequest, DatabaseTestResult
from app.schemas.product import ProductOut, ProductCreate
from app.schemas.order import OrderOut
from app.services import auth_service, product_service, order_service
import app.services.database_service as database_service
from app.models.user import User

router = APIRouter()


@router.get('/')
def admin_root():
  return {
    'message': 'Admin API root',
    'endpoints': [
      '/admin/users',
      '/admin/products',
      '/admin/orders',
      '/admin/database/test'
    ]
  }


@router.get('/users', response_model=list[UserOut], dependencies=[Depends(auth_service.get_current_admin)])
def list_users(db: Session = Depends(get_db)):
  return db.query(User).all()


@router.get('/products', response_model=list[ProductOut], dependencies=[Depends(auth_service.get_current_admin)])
def admin_products(db: Session = Depends(get_db)):
  return product_service.list_products(db)


@router.post('/products', response_model=ProductOut, dependencies=[Depends(auth_service.get_current_admin)])
def admin_create_product(payload: ProductCreate, db: Session = Depends(get_db)):
  return product_service.create_product(db, payload)


@router.put('/products/{product_id}', response_model=ProductOut, dependencies=[Depends(auth_service.get_current_admin)])
def admin_update_product(product_id: int, payload: ProductCreate, db: Session = Depends(get_db)):
  return product_service.update_product(db, product_id, payload)


@router.delete('/products/{product_id}', dependencies=[Depends(auth_service.get_current_admin)])
def admin_delete_product(product_id: int, db: Session = Depends(get_db)):
  product_service.delete_product(db, product_id)
  return {'status': 'deleted'}


@router.get('/orders', response_model=list[OrderOut], dependencies=[Depends(auth_service.get_current_admin)])
def admin_orders(db: Session = Depends(get_db)):
  return order_service.list_orders(db)


@router.get('/orders/{order_id}', response_model=OrderOut, dependencies=[Depends(auth_service.get_current_admin)])
def admin_order_detail(order_id: int, db: Session = Depends(get_db)):
  return order_service.get_order(db, order_id)


@router.post('/database/test', response_model=DatabaseTestResult, dependencies=[Depends(auth_service.get_current_admin)])
def admin_test_database(payload: DatabaseTestRequest):
  return database_service.test_mysql_connection(payload)
