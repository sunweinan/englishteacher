from __future__ import annotations

import json
from typing import Dict, Tuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.system_setting import SystemSetting
from app.models.integration import IntegrationConfig
from app.config import settings
from app.utils.seed_data import PERMISSION_COMMAND, persist_seed_config, SEED_DATA_DIR
from app.core.config_store import CONFIG_PATH, load_config, merge_config_updates
from app.core.install_state import INSTALL_PERMISSION_COMMAND, INSTALL_STATE_PATH, ensure_install_state_dir

DEFAULT_CONFIG = {
  'server_ip': '',
  'domain': '',
  'login_user': '',
  'login_password': '',
  'db_host': '',
  'db_port': 3306,
  'db_name': '',
  'db_user': '',
  'db_password': '',
  'root_password': '',
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


def _build_defaults_from_server_config() -> Dict[str, str | int]:
  data: Dict[str, str | int] = {**DEFAULT_CONFIG}
  server_config = load_config()
  site = server_config.get('site', {}) if isinstance(server_config, dict) else {}
  database = server_config.get('database', {}) if isinstance(server_config, dict) else {}

  if isinstance(site, dict):
    data['server_ip'] = site.get('ip', data['server_ip'])
    data['domain'] = site.get('domain', data['domain'])
  if isinstance(database, dict):
    data['db_host'] = database.get('host', data['db_host'])
    data['db_name'] = database.get('name', data['db_name'])
    data['db_user'] = database.get('user', data['db_user'])
    data['db_password'] = database.get('password', data['db_password'])
    data['root_password'] = database.get('root_password', data['root_password'])
    try:
      data['db_port'] = int(database.get('port', data['db_port']))
    except (TypeError, ValueError):
      pass
  return data


def get_config(db: Session) -> Dict[str, str | int]:
  data: Dict[str, str | int] = _build_defaults_from_server_config()
  try:
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
  except SQLAlchemyError:
    return data
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
    merged_config = merge_config_updates({
      'site': {
        'ip': payload.get('server_ip'),
        'domain': payload.get('domain'),
        'backend_port': settings.site_port,
      },
      'database': {
        'host': payload.get('db_host'),
        'port': payload.get('db_port'),
        'name': payload.get('db_name'),
        'user': payload.get('db_user'),
        'password': payload.get('db_password'),
        'root_password': payload.get('root_password'),
      }
    })
    # keep a snapshot for installer fallback
    state = {'config': merged_config}
    ensure_install_state_dir()
    with INSTALL_STATE_PATH.open('w', encoding='utf-8') as state_file:
      json.dump(state, state_file, ensure_ascii=False, indent=2)
  except PermissionError as exc:  # noqa: PERF203
    db.rollback()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
      'message': f'写入配置文件失败，请检查文件权限，或执行：{INSTALL_PERMISSION_COMMAND}',
      'code': 'INSTALL_STATE_PERMISSION_DENIED',
      'command': INSTALL_PERMISSION_COMMAND,
      'path': str(CONFIG_PATH)
    }) from exc
  except OSError as exc:  # noqa: PERF203
    db.rollback()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
      'message': '更新配置文件失败，请检查磁盘空间或路径。'
    }) from exc

  db.commit()
  return get_config(db)
