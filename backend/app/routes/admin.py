from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.admin import (
  AdminOrderOut,
  AdminPaymentRecord,
  AdminUserProfileOut,
  DashboardStat,
  DatabaseTestRequest,
  DatabaseTestResult,
  SystemConfig,
  SystemConfigUpdate
)
from app.schemas.course import CourseCreate, CourseOut
from app.schemas.product import ProductCreate, ProductOut
from app.services import auth_service, course_service, product_service
import app.services.admin_data_service as admin_data_service
import app.services.database_service as database_service
import app.services.system_config_service as system_config_service

router = APIRouter()


@router.get('/')
def admin_root():
  return {
    'message': 'Admin API root',
    'endpoints': [
      '/admin/dashboard',
      '/admin/users',
      '/admin/products',
      '/admin/orders',
      '/admin/database/test',
      '/admin/config'
    ]
  }


@router.get('/dashboard', response_model=list[DashboardStat], dependencies=[Depends(auth_service.get_current_admin)])
def dashboard(db: Session = Depends(get_db)):
  return admin_data_service.list_dashboard_stats(db)


@router.get('/users', response_model=list[AdminUserProfileOut], dependencies=[Depends(auth_service.get_current_admin)])
def list_users(db: Session = Depends(get_db)):
  return admin_data_service.list_admin_users(db)


@router.get('/payments', response_model=list[AdminPaymentRecord], dependencies=[Depends(auth_service.get_current_admin)])
def list_payments(db: Session = Depends(get_db)):
  return admin_data_service.list_recharge_records(db)


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


@router.get('/orders', response_model=list[AdminOrderOut], dependencies=[Depends(auth_service.get_current_admin)])
def admin_orders(db: Session = Depends(get_db)):
  return admin_data_service.list_admin_orders(db)


@router.get('/orders/{order_id}', response_model=AdminOrderOut, dependencies=[Depends(auth_service.get_current_admin)])
def admin_order_detail(order_id: str, db: Session = Depends(get_db)):
  return admin_data_service.get_admin_order(db, order_id)


@router.get('/courses', response_model=list[CourseOut], dependencies=[Depends(auth_service.get_current_admin)])
def admin_courses(db: Session = Depends(get_db)):
  return course_service.list_courses(db)


@router.post('/courses', response_model=CourseOut, dependencies=[Depends(auth_service.get_current_admin)])
def admin_create_course(payload: CourseCreate, db: Session = Depends(get_db)):
  return course_service.create_course(db, payload)


@router.put('/courses/{course_id}', response_model=CourseOut, dependencies=[Depends(auth_service.get_current_admin)])
def admin_update_course(course_id: int, payload: CourseCreate, db: Session = Depends(get_db)):
  return course_service.update_course(db, course_id, payload)


@router.delete('/courses/{course_id}', dependencies=[Depends(auth_service.get_current_admin)])
def admin_delete_course(course_id: int, db: Session = Depends(get_db)):
  course_service.delete_course(db, course_id)
  return {'status': 'deleted'}


@router.post('/database/test', response_model=DatabaseTestResult, dependencies=[Depends(auth_service.get_current_admin)])
def admin_test_database(payload: DatabaseTestRequest):
  return database_service.test_mysql_connection(payload)


@router.post('/database/seed', dependencies=[Depends(auth_service.get_current_admin)])
def admin_seed_database(db: Session = Depends(get_db)):
  return database_service.initialize_seed_data(db, overwrite_existing=False)


@router.get('/config', response_model=SystemConfig, dependencies=[Depends(auth_service.get_current_admin)])
def get_admin_config(db: Session = Depends(get_db)):
  return system_config_service.get_config(db)


@router.put('/config', response_model=SystemConfig, dependencies=[Depends(auth_service.get_current_admin)])
def save_admin_config(payload: SystemConfigUpdate, db: Session = Depends(get_db)):
  return system_config_service.save_config(db, payload.model_dump())
