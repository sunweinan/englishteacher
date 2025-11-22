from sqlalchemy import Column, Integer, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Order(Base):
  __tablename__ = 'orders'

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  total_amount = Column(Numeric(10, 2), default=0)
  status = Column(String(20), default='pending')

  items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')


class OrderItem(Base):
  __tablename__ = 'order_items'

  id = Column(Integer, primary_key=True, index=True)
  order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
  product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
  quantity = Column(Integer, default=1)
  price = Column(Numeric(10, 2), default=0)

  order = relationship('Order', back_populates='items')
