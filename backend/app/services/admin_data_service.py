from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.admin import AdminOrder, AdminUserProfile
from app.models.membership import AdminDashboardStat, RechargeRecord


def list_dashboard_stats(db: Session):
  try:
    return db.query(AdminDashboardStat).order_by(AdminDashboardStat.id.asc()).all()
  except SQLAlchemyError:
    return []


def list_admin_users(db: Session):
  try:
    return db.query(AdminUserProfile).order_by(AdminUserProfile.register_at.desc()).all()
  except SQLAlchemyError:
    return []


def list_recharge_records(db: Session):
  try:
    return db.query(RechargeRecord).order_by(RechargeRecord.paid_at.desc()).all()
  except SQLAlchemyError:
    return []


def list_admin_orders(db: Session):
  try:
    return db.query(AdminOrder).options(selectinload(AdminOrder.items)).order_by(AdminOrder.created_at.desc()).all()
  except SQLAlchemyError:
    return []


def get_admin_order(db: Session, order_id: str):
  try:
    order = (
      db.query(AdminOrder)
      .options(selectinload(AdminOrder.items))
      .filter(AdminOrder.id == order_id)
      .first()
    )
  except SQLAlchemyError:
    raise HTTPException(status_code=404, detail='订单数据不存在或尚未初始化。')
  if not order:
    raise HTTPException(status_code=404, detail='Order not found')
  return order
