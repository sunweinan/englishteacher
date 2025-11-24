from sqlalchemy import Column, DateTime, Integer, Numeric, String
from app.core.database import Base


class MembershipSetting(Base):
  __tablename__ = 'membership_settings'

  id = Column(Integer, primary_key=True, index=True)
  level = Column(String(50), unique=True, nullable=False)
  price = Column(Numeric(10, 2), nullable=False)
  duration_days = Column(Integer, default=0)
  description = Column(String(255), default='')


class RechargeRecord(Base):
  __tablename__ = 'recharge_records'

  id = Column(Integer, primary_key=True, index=True)
  user_display = Column(String(50), nullable=False)
  level = Column(String(50), nullable=False)
  amount = Column(Numeric(10, 2), nullable=False)
  channel = Column(String(50), default='')
  order_no = Column(String(64), unique=True, nullable=False)
  paid_at = Column(DateTime, nullable=False)


class AdminDashboardStat(Base):
  __tablename__ = 'admin_dashboard_stats'

  id = Column(Integer, primary_key=True, index=True)
  label = Column(String(100), unique=True, nullable=False)
  value = Column(String(50), default='')
  note = Column(String(255), default='')
