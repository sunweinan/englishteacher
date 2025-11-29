from __future__ import annotations

from typing import Any, Dict, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config_store import CONFIG_PATH, merge_config_updates
from app.core.install_state import INSTALL_STATE_PATH, save_install_state
from app.schemas.install import InstallRequest
from app.installer.database_initializer import create_schema, seed_all
from app.utils.seed_data import PERMISSION_COMMAND, SEED_DATA_DIR, persist_seed_config


class InstallProgressError(HTTPException):
  def __init__(self, step: str, message: str, progress: list[Dict[str, str]] | None = None,
               status_code: int = status.HTTP_400_BAD_REQUEST, code: str | None = None,
               command: str | None = None, path: str | None = None):
    detail: Dict[str, Any] = {'step': step, 'message': message}
    if progress is not None:
      detail['progress'] = progress
    if code:
      detail['code'] = code
    if command:
      detail['command'] = command
    if path:
      detail['path'] = path
    super().__init__(status_code=status_code, detail=detail)


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


STEP_LABELS = {
  'connect_root': '登录 MySQL root',
  'provision_db': '创建数据库和账号',
  'init_schema': '初始化表结构',
  'seed_data': '写入预置数据',
  'write_config': '写入配置文件'
}


def _create_app_engine(host: str, port: int, user: str, password: str, db_name: str):
  return create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}",
    echo=False,
    future=True
  )


def _persist_install_state(payload: InstallRequest) -> None:
  save_install_state({
    'installed': True,
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
  })


def _persist_seed_files(payload: InstallRequest, host: str, port: int) -> None:
  persist_seed_config({
    'server_ip': payload.server_ip,
    'domain': payload.server_domain,
    'login_user': payload.admin_username,
    'login_password': payload.admin_password,
    'db_host': host,
    'db_port': port,
    'db_name': payload.database_name,
    'db_user': payload.database_user,
    'db_password': payload.database_password,
    'root_password': payload.mysql_root_password,
  }, backend_port=payload.backend_port)


def _assert_root_connection(engine, progress: list[Dict[str, str]]) -> None:
  try:
    with engine.connect():
      return
  except OperationalError as exc:  # noqa: PERF203
    message = '无法连接到 MySQL，请确认主机和 root 密码是否正确。'
    if 'Access denied' in str(exc.orig):
      message = 'root 密码错误，无法连接 MySQL。'
    raise InstallProgressError('connect_root', message, progress) from exc


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
  progress: list[Dict[str, str]] = []

  def _record_step(step: str) -> None:
    if step in STEP_LABELS:
      progress.append({'step': step, 'label': STEP_LABELS[step]})

  host, port = _resolve_mysql_host_port(payload)
  root_engine = _create_root_engine(host, port, payload.mysql_root_password)
  _assert_root_connection(root_engine, progress)
  _record_step('connect_root')

  try:
    _create_database_and_user(root_engine, payload, host)
  except OperationalError as exc:  # noqa: PERF203
    message = '创建数据库或账号失败，请确认 root 权限。'
    raise InstallProgressError('provision_db', message, progress) from exc
  _record_step('provision_db')

  app_engine = _create_app_engine(host, port, payload.database_user, payload.database_password, payload.database_name)
  try:
    SessionLocal = create_schema(app_engine)
  except OperationalError as exc:  # noqa: PERF203
    raise InstallProgressError('init_schema', '业务账号无法连接数据库，请检查账号密码或授权。', progress) from exc
  _record_step('init_schema')

  db: Session = SessionLocal()
  try:
    seed_all(db, admin_payload={'username': payload.admin_username, 'password': payload.admin_password}, settings_overrides={
      'domain': payload.server_domain,
      'ip': payload.server_ip,
      'backend_port': str(payload.backend_port)
    }, integrations={
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
    })
  except PermissionError as exc:  # noqa: PERF203
    raise InstallProgressError('seed_data', '写入数据库时权限不足，请检查账户授权。', progress) from exc
  finally:
    db.close()
  _record_step('seed_data')

  try:
    _persist_install_state(payload)
    merge_config_updates({
      'site': {
        'domain': payload.server_domain,
        'ip': payload.server_ip,
        'backend_port': payload.backend_port
      },
      'database': {
        'host': host,
        'port': port,
        'name': payload.database_name,
        'user': payload.database_user,
        'password': payload.database_password,
        'root_password': payload.mysql_root_password
      }
    })
    _persist_seed_files(payload, host, port)
  except PermissionError as exc:  # noqa: PERF203
    raise InstallProgressError(
      'write_config',
      f'写入配置文件失败，请检查目录读写权限，或执行：{PERMISSION_COMMAND}',
      progress,
      code='SEED_DATA_PERMISSION_DENIED',
      command=PERMISSION_COMMAND,
      path=str(SEED_DATA_DIR)
    ) from exc
  except OSError as exc:  # noqa: PERF203
    raise InstallProgressError(
      'write_config',
      '写入配置文件失败，请确认目录存在且有可用空间。',
      progress,
      code='CONFIG_WRITE_FAILED',
      path=str(CONFIG_PATH)
    ) from exc
  _record_step('write_config')

  return {
    'success': True,
    'message': '安装完成，配置和预置数据已写入。',
    'next_url': '/admin/login',
    'progress': progress
  }


def test_mysql_connection(database_url: str) -> bool:
  try:
    engine = create_engine(database_url, echo=False, future=True)
    with engine.connect():
      return True
  except Exception:
    return False
