from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.product import Product
from app.schemas.product import ProductCreate


def list_products(db: Session, q: str | None = None):
  query = db.query(Product)
  if q:
    query = query.filter(Product.name.ilike(f"%{q}%"))
  return query.all()


def get_product(db: Session, product_id: int) -> Product:
  product = db.query(Product).filter(Product.id == product_id).first()
  if not product:
    raise HTTPException(status_code=404, detail='Product not found')
  return product


def create_product(db: Session, product_in: ProductCreate) -> Product:
  product = Product(**product_in.model_dump())
  db.add(product)
  db.commit()
  db.refresh(product)
  return product


def update_product(db: Session, product_id: int, product_in: ProductCreate) -> Product:
  product = get_product(db, product_id)
  for key, value in product_in.model_dump().items():
    setattr(product, key, value)
  db.commit()
  db.refresh(product)
  return product


def delete_product(db: Session, product_id: int):
  product = get_product(db, product_id)
  db.delete(product)
  db.commit()
