import pymysql
from fastapi import HTTPException, status
from pymysql.err import OperationalError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import engine
from app.installer.database_initializer import create_schema, seed_all
from app.services import system_config_service

from app.schemas.admin import DatabaseTestRequest, DatabaseTestResult


def _connect(**kwargs):
  return pymysql.connect(connect_timeout=5, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, **kwargs)


def test_mysql_connection(payload: DatabaseTestRequest) -> DatabaseTestResult:
  if not payload.host.strip():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='请填写数据库地址后再检测。')
  if not payload.root_password.strip():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='请填写默认 root 密码后再检测。')

  root_conn = None
  try:
    root_conn = _connect(host=payload.host, port=payload.port, user='root', password=payload.root_password)
    root_connected = True
  except OperationalError as exc:  # noqa: PERF203
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='无法连接到 MySQL，请确认地址和默认 root 密码是否正确。'
    ) from exc

  database_exists = False
  database_authenticated = False

  try:
    if payload.db_name and payload.db_user and payload.db_password:
      with root_conn.cursor() as cursor:  # type: ignore[var-annotated]
        cursor.execute('SHOW DATABASES LIKE %s', (payload.db_name,))
        database_exists = cursor.fetchone() is not None

      user_conn = None
      try:
        user_conn = _connect(
          host=payload.host,
          port=payload.port,
          user=payload.db_user,
          password=payload.db_password,
          database=payload.db_name
        )
        database_authenticated = True
      except OperationalError as exc:  # noqa: PERF203
        message = exc.args[1] if len(exc.args) > 1 else str(exc)
        raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=f'无法使用账号 {payload.db_user} 连接数据库 {payload.db_name}：{message}'
        ) from exc
      finally:
        if user_conn:
          try:
            user_conn.close()
          except Exception:  # noqa: BLE001
            pass

      summary = '已成功连接 MySQL，root 密码和业务账号均可用。'
      if not database_exists:
        summary += ' 提醒：当前数据库名称不存在，请确认是否需要创建。'
    else:
      summary = '已成功连接 MySQL，root 密码可用。未提供业务数据库信息，已跳过数据库与账号验证。'

    return DatabaseTestResult(
      root_connected=root_connected,
      database_exists=database_exists,
      database_authenticated=database_authenticated,
      message=summary
    )
  finally:
    if root_conn:
      try:
        root_conn.close()
      except Exception:  # noqa: BLE001
        pass


def initialize_seed_data(db: Session, *, overwrite_existing: bool = False) -> dict:
  """Create tables if missing and load seed data without overwriting conflicting rows."""

  SessionLocal = create_schema(engine)
  seed_db = SessionLocal()
  try:
    config = system_config_service.get_config(db)
    seed_all(
      seed_db,
      admin_payload={
        'username': config.get('login_user', 'admin'),
        'password': config.get('login_password', 'Admin@123')
      },
      settings_overrides={
        'domain': config.get('domain'),
        'ip': config.get('server_ip'),
        'backend_port': str(settings.site_port),
      },
      integrations={'wechat': {}, 'sms': {}},
      overwrite_existing=overwrite_existing,
    )
    return {'status': 'ok', 'message': '数据库结构已检查完毕，预置数据同步完成。'}
  except SQLAlchemyError as exc:  # noqa: PERF203
    seed_db.rollback()
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail='初始化数据库失败，请检查数据库配置。'
    ) from exc
  finally:
    seed_db.close()
