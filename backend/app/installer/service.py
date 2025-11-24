from __future__ import annotations

import json
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.core.install_state import INSTALL_STATE_PATH, save_install_state
from app.schemas.install import InstallRequest
from app.installer import seeder


class InstallProgressError(HTTPException):
  def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
    super().__init__(status_code=status_code, detail=message)


def _resolve_mysql_host_port(payload: InstallRequest) -> Tuple[str, int]:
  if payload.mysql_url:
    parsed = urlparse(payload.mysql_url)
    host = parsed.hostname or payload.mysql_host or '127.0.0.1'
    port = parsed.port or payload.mysql_port or 3306
    return host, port
  return payload.mysql_host or '127.0.0.1', payload.mysql_port or 3306


def _create_root_engine(host: str, port: int, root_password: str):
  return create_engine(
    f"mysql+pymysql://root:{root_password}@{host}:{port}/",
    echo=False,
    future=True,
    isolation_level='AUTOCOMMIT'
  )


def _create_app_engine(host: str, port: int, user: str, password: str, db_name: str):
  return create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}",
    echo=False,
    future=True
  )


def _persist_install_config(payload: InstallRequest, host: str, port: int) -> None:
  state = {
    'installed': True,
    'config': {
      'database': {
        'user': payload.database_user,
        'password': payload.database_password,
        'host': host,
        'port': port,
        'name': payload.database_name,
      },
      'site': {
        'ip': payload.server_ip,
        'domain': payload.server_domain,
        'backend_port': payload.backend_port,
      }
    },
    'admin': {
      'username': payload.admin_username,
      'password': payload.admin_password
    },
    'integrations': {
      'wechat': {
        'app_id': payload.wechat_app_id,
        'mch_id': payload.wechat_mch_id,
        'api_key': payload.wechat_api_key
      },
      'sms': {
        'provider': payload.sms_provider,
        'api_key': payload.sms_api_key,
        'sign_name': payload.sms_sign_name
      }
    }
  }
  save_install_state(state)


def _write_server_file(payload: InstallRequest, host: str, port: int) -> None:
  INSTALL_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
  server_file = INSTALL_STATE_PATH.parent / 'server.json'
  data = {
    'server_domain': payload.server_domain,
    'server_ip': payload.server_ip,
    'backend_port': payload.backend_port,
    'mysql_host': host,
    'mysql_port': port
  }
  with server_file.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


def _init_schema(engine) -> Session:
  Base.metadata.create_all(bind=engine)
  SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
  return SessionLocal()


def _assert_root_connection(engine) -> None:
  try:
    with engine.connect():
      return
  except OperationalError as exc:  # noqa: PERF203
    message = '无法连接到 MySQL，请确认主机和 root 密码是否正确。'
    if 'Access denied' in str(exc.orig):
      message = 'root 密码错误，无法连接 MySQL。'
    raise InstallProgressError(message) from exc


def _create_database_and_user(root_engine, payload: InstallRequest, host: str) -> None:
  db_name = payload.database_name
  db_user = payload.database_user
  db_password = payload.database_password
  with root_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    conn.execute(text(f"CREATE USER IF NOT EXISTS '{db_user}'@'%' IDENTIFIED BY :pwd"), {'pwd': db_password})
    conn.execute(text(f"ALTER USER '{db_user}'@'%' IDENTIFIED BY :pwd"), {'pwd': db_password})
    conn.execute(text(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'%'"))
    conn.execute(text('FLUSH PRIVILEGES'))


def run_installation(payload: InstallRequest) -> Dict[str, Any]:
  host, port = _resolve_mysql_host_port(payload)
  root_engine = _create_root_engine(host, port, payload.mysql_root_password)
  _assert_root_connection(root_engine)

  try:
    _create_database_and_user(root_engine, payload, host)
  except OperationalError as exc:  # noqa: PERF203
    message = '创建数据库或账号失败，请确认 root 权限。'
    raise InstallProgressError(message) from exc

  app_engine = _create_app_engine(host, port, payload.database_user, payload.database_password, payload.database_name)
  try:
    db = _init_schema(app_engine)
  except OperationalError as exc:  # noqa: PERF203
    raise InstallProgressError('业务账号无法连接数据库，请检查账号密码或授权。') from exc

  try:
    seeder.seed_products(db)
    seeder.seed_users(db, {'username': payload.admin_username, 'password': payload.admin_password})
    seeder.seed_settings(db, {
      'domain': payload.server_domain,
      'ip': payload.server_ip,
      'backend_port': str(payload.backend_port)
    })
    seeder.seed_integrations(db, {
      'app_id': payload.wechat_app_id,
      'mch_id': payload.wechat_mch_id,
      'api_key': payload.wechat_api_key
    }, {
      'provider': payload.sms_provider,
      'api_key': payload.sms_api_key,
      'sign_name': payload.sms_sign_name
    })
  except PermissionError as exc:  # noqa: PERF203
    raise InstallProgressError('写入数据库时权限不足，请检查账户授权。') from exc
  finally:
    db.close()

  try:
    _persist_install_config(payload, host, port)
    _write_server_file(payload, host, port)
  except PermissionError as exc:  # noqa: PERF203
    raise InstallProgressError('写入配置文件失败，请检查目录读写权限。') from exc

  return {
    'success': True,
    'message': '安装完成，配置和预置数据已写入。',
    'next_url': '/admin/login'
  }


def test_mysql_connection(database_url: str) -> bool:
  try:
    engine = create_engine(database_url, echo=False, future=True)
    with engine.connect():
      return True
  except Exception:
    return False
