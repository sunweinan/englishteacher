from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Iterable, List

from sqlalchemy.orm import Session

from app.models.integration import IntegrationConfig
from app.models.membership import AdminDashboardStat, MembershipSetting, RechargeRecord
from app.models.product import Product
from app.models.system_setting import SystemSetting
from app.models.user import User
from app.services.auth_service import get_password_hash

SEED_ROOT = Path(__file__).resolve().parent.parent / 'install' / 'seed_data'


def _read_json(filename: str) -> list[Dict[str, Any]]:
  path = SEED_ROOT / filename
  if not path.exists():
    return []
  with path.open('r', encoding='utf-8') as f:
    return json.load(f)


def seed_products(db: Session) -> None:
  data = _read_json('products.json')
  for item in data:
    exists = db.query(Product).filter(Product.name == item.get('name')).first()
    if exists:
      continue
    product = Product(**item)
    db.add(product)
  db.commit()


def seed_users(db: Session, admin_payload: Dict[str, str]) -> None:
  for item in _read_json('users.json'):
    exists = db.query(User).filter(User.username == item.get('username')).first()
    if exists:
      continue
    db.add(User(username=item['username'], password_hash=get_password_hash(item['password']), role=item.get('role', 'user')))

  admin_exists = db.query(User).filter(User.username == admin_payload['username']).first()
  if not admin_exists:
    db.add(User(username=admin_payload['username'], password_hash=get_password_hash(admin_payload['password']), role='admin'))
  db.commit()


def seed_settings(db: Session, overrides: Dict[str, str]) -> None:
  settings: Iterable[Dict[str, str]] = _read_json('system_settings.json')
  for setting in settings:
    merged_value = overrides.get(setting['key']) if overrides.get(setting['key']) is not None else setting['value']
    exists = db.query(SystemSetting).filter(SystemSetting.category == setting['category'], SystemSetting.key == setting['key']).first()
    if exists:
      exists.value = str(merged_value)
      db.add(exists)
      continue
    db.add(SystemSetting(category=setting['category'], key=setting['key'], value=str(merged_value), description=setting.get('description', '')))
  db.commit()


def seed_integrations(db: Session, wechat_config: Dict[str, Any], sms_config: Dict[str, Any]) -> None:
  integrations: List[Dict[str, Any]] = _read_json('integrations.json')
  for entry in integrations:
    provider = entry.get('provider')
    config = entry.get('config', {})
    is_active = entry.get('is_active', True)
    label = entry.get('label', provider)

    if provider == 'wechat_pay':
      config.update({
        'appId': wechat_config.get('app_id'),
        'mchId': wechat_config.get('mch_id'),
        'apiKey': wechat_config.get('api_key')
      })
      is_active = bool(wechat_config.get('app_id') and wechat_config.get('mch_id'))
    if provider == 'sms':
      config.update({
        'provider': sms_config.get('provider'),
        'apiKey': sms_config.get('api_key'),
        'signName': sms_config.get('sign_name')
      })
      is_active = bool(sms_config.get('provider'))

    existing = db.query(IntegrationConfig).filter(IntegrationConfig.provider == provider).first()
    if existing:
      existing.config = config
      existing.is_active = is_active
      existing.label = label
      db.add(existing)
      continue
    db.add(IntegrationConfig(provider=provider, config=config, is_active=is_active, label=label))
  db.commit()


def seed_membership_settings(db: Session) -> None:
  settings: List[Dict[str, Any]] = _read_json('membership_settings.json')
  for setting in settings:
    existing = db.query(MembershipSetting).filter(MembershipSetting.level == setting['level']).first()
    if existing:
      existing.price = setting['price']
      existing.duration_days = setting.get('duration_days', 0)
      existing.description = setting.get('description', '')
      db.add(existing)
      continue
    db.add(MembershipSetting(**setting))
  db.commit()


def seed_recharge_records(db: Session) -> None:
  records: List[Dict[str, Any]] = _read_json('admin_payments.json')
  for record in records:
    order_no = record['orderNo']
    existing = db.query(RechargeRecord).filter(RechargeRecord.order_no == order_no).first()
    paid_at = datetime.fromisoformat(record['time'])
    payload = {
      'user_display': record['user'],
      'level': record['level'],
      'amount': record['amount'],
      'channel': record.get('channel', ''),
      'order_no': order_no,
      'paid_at': paid_at
    }
    if existing:
      for key, value in payload.items():
        setattr(existing, key, value)
      db.add(existing)
      continue
    db.add(RechargeRecord(**payload))
  db.commit()


def seed_dashboard_stats(db: Session) -> None:
  stats: List[Dict[str, Any]] = _read_json('admin_dashboard_stats.json')
  for entry in stats:
    existing = db.query(AdminDashboardStat).filter(AdminDashboardStat.label == entry['label']).first()
    if existing:
      existing.value = entry.get('value', '')
      existing.note = entry.get('note', '')
      db.add(existing)
      continue
    db.add(AdminDashboardStat(label=entry['label'], value=entry.get('value', ''), note=entry.get('note', '')))
  db.commit()
