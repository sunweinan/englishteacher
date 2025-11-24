from __future__ import annotations

from typing import Dict, Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.system_setting import SystemSetting
from app.models.integration import IntegrationConfig
from app.config import settings
from app.utils.seed_data import PERMISSION_COMMAND, persist_seed_config, SEED_DATA_DIR
from app.core.install_state import INSTALL_PERMISSION_COMMAND, INSTALL_STATE_PATH, update_install_state

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
  'root_password': 'Ad123456',
  'wechat_app_id': '',
  'wechat_mch_id': '',
  'wechat_api_key': '',
  'sms_provider': '',
  'sms_api_key': '',
  'sms_sign_name': ''
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

_INTEGRATION_DEFAULTS: Dict[str, Dict[str, str]] = {
  'wechat_pay': {
    'appId': '',
    'mchId': '',
    'apiKey': ''
  },
  'sms': {
    'provider': '',
    'apiKey': '',
    'signName': ''
  }
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


def _get_integration_config(db: Session, provider: str) -> Dict[str, str]:
  record = db.query(IntegrationConfig).filter(IntegrationConfig.provider == provider).first()
  if record and isinstance(record.config, dict):
    return {**_INTEGRATION_DEFAULTS.get(provider, {}), **record.config}
  return _INTEGRATION_DEFAULTS.get(provider, {})


def _upsert_integration_config(db: Session, provider: str, *, label: str, config: Dict[str, str], is_active: bool) -> None:
  record = db.query(IntegrationConfig).filter(IntegrationConfig.provider == provider).first()
  payload = {
    'provider': provider,
    'label': label,
    'config': config,
    'is_active': is_active
  }
  if record:
    for key, value in payload.items():
      setattr(record, key, value)
    db.add(record)
    return
  db.add(IntegrationConfig(**payload))


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
  wechat_config = _get_integration_config(db, 'wechat_pay')
  sms_config = _get_integration_config(db, 'sms')

  data['wechat_app_id'] = wechat_config.get('appId', '')
  data['wechat_mch_id'] = wechat_config.get('mchId', '')
  data['wechat_api_key'] = wechat_config.get('apiKey', '')

  data['sms_provider'] = sms_config.get('provider', '')
  data['sms_api_key'] = sms_config.get('apiKey', '')
  data['sms_sign_name'] = sms_config.get('signName', '')
  return data


def save_config(db: Session, payload: Dict[str, str | int]) -> Dict[str, str | int]:
  for field, (category, key) in _SETTING_KEYS.items():
    value = payload.get(field)
    if value is None:
      continue
    _upsert_setting(db, category, key, str(value))

  _upsert_integration_config(
    db,
    'wechat_pay',
    label='微信支付',
    config={
      'appId': str(payload.get('wechat_app_id', '') or ''),
      'mchId': str(payload.get('wechat_mch_id', '') or ''),
      'apiKey': str(payload.get('wechat_api_key', '') or '')
    },
    is_active=bool(payload.get('wechat_app_id') and payload.get('wechat_mch_id'))
  )

  _upsert_integration_config(
    db,
    'sms',
    label='短信服务',
    config={
      'provider': str(payload.get('sms_provider', '') or ''),
      'apiKey': str(payload.get('sms_api_key', '') or ''),
      'signName': str(payload.get('sms_sign_name', '') or '')
    },
    is_active=bool(payload.get('sms_provider'))
  )
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

  try:
    update_install_state({
      'database': {
        'user': payload.get('db_user'),
        'password': payload.get('db_password'),
        'host': payload.get('db_host'),
        'port': payload.get('db_port'),
        'name': payload.get('db_name')
      },
      'site': {
        'ip': payload.get('server_ip'),
        'domain': payload.get('domain'),
      }
    })
  except PermissionError as exc:  # noqa: PERF203
    db.rollback()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
      'message': f'写入 installation.json 失败，请检查文件权限，或执行：{INSTALL_PERMISSION_COMMAND}',
      'code': 'INSTALL_STATE_PERMISSION_DENIED',
      'command': INSTALL_PERMISSION_COMMAND,
      'path': str(INSTALL_STATE_PATH)
    }) from exc

  db.commit()
  return get_config(db)
