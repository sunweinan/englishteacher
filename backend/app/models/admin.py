from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class AdminUserProfile(Base):
  __tablename__ = 'admin_user_profiles'

  id = Column(Integer, primary_key=True, index=True)
  nickname = Column(String(100), nullable=False)
  phone = Column(String(50), unique=True, nullable=False)
  level = Column(String(50), nullable=False)
  register_at = Column(DateTime, nullable=False)
  spend = Column(Numeric(10, 2), default=0)
  tests = Column(Integer, default=0)
  benefits = Column(Text, default='')
  recharges = Column(JSON, default=[])
  note = Column(String(255), default='')


class AdminOrder(Base):
  __tablename__ = 'admin_orders'

  id = Column(String(64), primary_key=True, index=True)
  user = Column(String(100), nullable=False)
  created_at = Column(DateTime, nullable=False)
  status = Column(String(20), default='待支付')
  channel = Column(String(50), default='')
  amount = Column(Numeric(10, 2), nullable=False)
  remark = Column(Text, default='')

  items = relationship('AdminOrderItem', back_populates='order', cascade='all, delete-orphan')


class AdminOrderItem(Base):
  __tablename__ = 'admin_order_items'

  id = Column(Integer, primary_key=True, index=True)
  order_id = Column(String(64), ForeignKey('admin_orders.id'), nullable=False)
  name = Column(String(200), nullable=False)
  quantity = Column(Integer, default=1)
  price = Column(Numeric(10, 2), default=0)

  order = relationship('AdminOrder', back_populates='items')


class Course(Base):
  __tablename__ = 'courses'

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String(200), nullable=False)
  subtitle = Column(String(255), default='')
  tag = Column(String(50), default='')
  image = Column(String(500), default='')

  lessons = relationship('CourseLesson', back_populates='course', cascade='all, delete-orphan')


class CourseLesson(Base):
  __tablename__ = 'course_lessons'

  id = Column(Integer, primary_key=True, index=True)
  course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
  zh = Column(String(255), nullable=False)
  en = Column(String(255), nullable=False)
  phonetic = Column(String(255), default='')
  audio = Column(String(255), default='')

  course = relationship('Course', back_populates='lessons')
