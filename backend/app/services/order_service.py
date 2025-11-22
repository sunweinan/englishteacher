from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate


def create_order(db: Session, user_id: int, order_in: OrderCreate) -> Order:
  total = Decimal('0')
  order = Order(user_id=user_id, status='pending')
  db.add(order)
  db.flush()
  for item in order_in.items:
    product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
    if not product or product.stock < item.quantity:
      raise HTTPException(status_code=400, detail='Insufficient stock')
    product.stock -= item.quantity
    line_total = Decimal(product.price) * item.quantity
    total += line_total
    db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, price=product.price))
  order.total_amount = total
  db.commit()
  db.refresh(order)
  return order


def get_order(db: Session, order_id: int, user_id: int | None = None) -> Order:
  query = db.query(Order).filter(Order.id == order_id)
  if user_id:
    query = query.filter(Order.user_id == user_id)
  order = query.first()
  if not order:
    raise HTTPException(status_code=404, detail='Order not found')
  return order


def list_orders(db: Session, user_id: int | None = None):
  query = db.query(Order)
  if user_id:
    query = query.filter(Order.user_id == user_id)
  return query.all()
