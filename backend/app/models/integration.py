from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.mysql import JSON
from app.core.database import Base


class IntegrationConfig(Base):
  __tablename__ = 'integration_configs'

  id = Column(Integer, primary_key=True, index=True)
  provider = Column(String(50), nullable=False, index=True)
  label = Column(String(100), default='')
  is_active = Column(Boolean, default=True)
  config = Column(JSON, default={})
