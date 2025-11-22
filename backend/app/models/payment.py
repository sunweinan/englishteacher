from sqlalchemy import Column, Integer, ForeignKey, String
from app.core.database import Base


class Payment(Base):
  __tablename__ = 'payments'

  id = Column(Integer, primary_key=True, index=True)
  order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
  provider = Column(String(50), default='wechat')
  status = Column(String(20), default='pending')
  raw_notify = Column(String(2000), default='')
