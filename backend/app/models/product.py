from sqlalchemy import Column, Integer, String, Text, Numeric
from app.core.database import Base


class Product(Base):
  __tablename__ = 'products'

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(100), nullable=False)
  description = Column(Text, default='')
  price = Column(Numeric(10, 2), nullable=False)
  stock = Column(Integer, default=0)
