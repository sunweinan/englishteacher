from datetime import datetime
import json
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.admin import AdminOrder, AdminUserProfile
from app.models.membership import AdminDashboardStat, RechargeRecord

SEED_DIR = Path(__file__).resolve().parent.parent / 'install' / 'seed_data'


def _load_seed(filename: str) -> list[dict]:
  path = SEED_DIR / filename
  if not path.exists():
    return []
  with path.open('r', encoding='utf-8') as file:
    return json.load(file)


def list_dashboard_stats(db: Session):
  try:
    stats = db.query(AdminDashboardStat).order_by(AdminDashboardStat.id.asc()).all()
    if stats:
      return stats
  except SQLAlchemyError:
    stats = []

  seed_items = _load_seed('admin_dashboard_stats.json')
  return [{'label': item.get('label', ''), 'value': item.get('value', ''), 'note': item.get('note', '')} for item in seed_items]


def list_admin_users(db: Session):
  try:
    users = db.query(AdminUserProfile).order_by(AdminUserProfile.register_at.desc()).all()
    if users:
      return users
  except SQLAlchemyError:
    users = []

  seed_items = _load_seed('admin_users.json')
  profiles: list[dict] = []
  for item in seed_items:
    try:
      register_at = datetime.fromisoformat(item.get('registerAt', ''))
    except ValueError:
      continue
    profiles.append({
      'id': item.get('id'),
      'nickname': item.get('nickname', ''),
      'phone': item.get('phone', ''),
      'level': item.get('level', ''),
      'register_at': register_at,
      'spend': item.get('spend', 0),
      'tests': item.get('tests', 0),
      'benefits': item.get('benefits', ''),
      'recharges': item.get('recharges', []),
      'note': item.get('note')
    })
  return profiles


def list_recharge_records(db: Session):
  try:
    records = db.query(RechargeRecord).order_by(RechargeRecord.paid_at.desc()).all()
    if records:
      return records
  except SQLAlchemyError:
    records = []

  seed_items = _load_seed('admin_payments.json')
  payments: list[dict] = []
  for item in seed_items:
    try:
      paid_at = datetime.fromisoformat(item.get('time', ''))
    except ValueError:
      continue
    payments.append({
      'user_display': item.get('user', ''),
      'level': item.get('level', ''),
      'amount': item.get('amount', 0),
      'channel': item.get('channel', ''),
      'order_no': item.get('orderNo', ''),
      'paid_at': paid_at
    })
  return payments


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
