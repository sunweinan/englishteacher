from __future__ import annotations

from typing import Dict, Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.system_setting import SystemSetting
from app.config import settings
from app.utils.seed_data import PERMISSION_COMMAND, persist_seed_config, SEED_DATA_DIR

DEFAULT_CONFIG = {
  'server_ip': '10.10.10.8',
  'domain': 'english.example.com',
  'login_user': 'root',
  'login_password': 'Admin@123',
  'db_host': '127.0.0.1',
  'db_port': 3306,
  'db_name': 'english_db',
  'db_user': 'english_user',
  'db_password': 'db_pass_123',
  'root_password': 'Ad123456'
}

_SETTING_KEYS: Dict[str, Tuple[str, str]] = {
  'server_ip': ('site', 'ip'),
  'domain': ('site', 'domain'),
  'login_user': ('auth', 'login_user'),
  'login_password': ('auth', 'login_password'),
  'db_host': ('database', 'host'),
  'db_port': ('database', 'port'),
  'db_name': ('database', 'name'),
  'db_user': ('database', 'user'),
  'db_password': ('database', 'password'),
  'root_password': ('database', 'root_password')
}


def _get_setting(db: Session, category: str, key: str) -> str | None:
  record = db.query(SystemSetting).filter(
    SystemSetting.category == category,
    SystemSetting.key == key
  ).first()
  return record.value if record and record.value is not None else None


def _upsert_setting(db: Session, category: str, key: str, value: str) -> None:
  record = db.query(SystemSetting).filter(
    SystemSetting.category == category,
    SystemSetting.key == key
  ).first()
  if record:
    record.value = value
    db.add(record)
    return
  db.add(SystemSetting(category=category, key=key, value=value))


def get_config(db: Session) -> Dict[str, str | int]:
  data: Dict[str, str | int] = {**DEFAULT_CONFIG}
  for field, (category, key) in _SETTING_KEYS.items():
    stored = _get_setting(db, category, key)
    if stored is None:
      continue
    if field == 'db_port':
      try:
        data[field] = int(stored)
      except (TypeError, ValueError):
        continue
    else:
      data[field] = stored
  return data


def save_config(db: Session, payload: Dict[str, str | int]) -> Dict[str, str | int]:
  for field, (category, key) in _SETTING_KEYS.items():
    value = payload.get(field)
    if value is None:
      continue
    _upsert_setting(db, category, key, str(value))
  try:
    persist_seed_config(payload, backend_port=settings.site_port)
  except PermissionError as exc:  # noqa: PERF203
    db.rollback()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
      'message': f'写入 seed_data 目录失败，请检查文件权限，或执行：{PERMISSION_COMMAND}',
      'code': 'SEED_DATA_PERMISSION_DENIED',
      'command': PERMISSION_COMMAND,
      'path': str(SEED_DATA_DIR)
    }) from exc

  db.commit()
  return get_config(db)
