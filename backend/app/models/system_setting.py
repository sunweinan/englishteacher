from sqlalchemy import Column, Integer, String, Text, UniqueConstraint

from app.core.database import Base


class SystemSetting(Base):
  __tablename__ = 'system_settings'
  __table_args__ = (
    UniqueConstraint('category', 'key', name='uq_system_setting_category_key'),
  )

  id = Column(Integer, primary_key=True, index=True)
  category = Column(String(50), nullable=False, index=True)
  key = Column(String(100), nullable=False, index=True)
  value = Column(Text, default='')
  description = Column(String(255), default='')
