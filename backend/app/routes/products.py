from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.product import ProductOut, ProductCreate
from app.services import product_service, auth_service

router = APIRouter()


@router.get('/', response_model=list[ProductOut])
def list_products(q: str | None = None, db: Session = Depends(get_db)):
  return product_service.list_products(db, q)


@router.get('/{product_id}', response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
  return product_service.get_product(db, product_id)


@router.post('/', response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _: str = Depends(auth_service.get_current_admin)):
  return product_service.create_product(db, payload)


@router.put('/{product_id}', response_model=ProductOut)
def update_product(product_id: int, payload: ProductCreate, db: Session = Depends(get_db), _: str = Depends(auth_service.get_current_admin)):
  return product_service.update_product(db, product_id, payload)


@router.delete('/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db), _: str = Depends(auth_service.get_current_admin)):
  product_service.delete_product(db, product_id)
  return {'status': 'deleted'}
