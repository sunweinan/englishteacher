from sqlalchemy import Column, DateTime, Integer, String
from datetime import datetime
from app.core.database import Base


class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, index=True)
  username = Column(String(50), unique=True, index=True, nullable=False)
  phone = Column(String(20), unique=True, index=True, nullable=True)
  password_hash = Column(String(255), nullable=False)
  role = Column(String(20), default='user')
  membership_level = Column(String(50), default='free')
  membership_expires_at = Column(DateTime, nullable=True)
  created_at = Column(DateTime, default=datetime.utcnow)
