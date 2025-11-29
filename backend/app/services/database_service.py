from fastapi import HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import engine
from app.installer.database_initializer import create_schema, seed_all
from app.schemas.admin import DatabaseTestRequest, DatabaseTestResult
from app.schemas.install import MysqlConnectionTestResult
from app.services import system_config_service


def test_mysql_connection(payload: DatabaseTestRequest) -> MysqlConnectionTestResult:
  url = f"mysql+pymysql://root:{payload.root_password}@{payload.host}:{payload.port}"
  engine = create_engine(url)

  try:
    with engine.connect() as conn:
      conn.execute(text('SELECT 1'))
    return DatabaseTestResult(
      root_connected=True,
      database_exists=False,
      database_authenticated=False,
      message='已完成 root 连接验证，已跳过业务数据库检查。'
    )
  except Exception as exc:  # noqa: BLE001
    return DatabaseTestResult(
      root_connected=False,
      database_exists=False,
      database_authenticated=False,
      message=str(exc)
    )


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
