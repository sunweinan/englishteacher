from fastapi import APIRouter, HTTPException

from sqlalchemy import create_engine, text

from app.config import settings
from app.schemas.install import (
  InstallRequest,
  InstallResult,
  InstallStatus,
  MysqlConnectionTestRequest,
  MysqlConnectionTestResult,
)
from app.installer import service as installer_service
from app.core.install_state import load_install_state

router = APIRouter(prefix='/install', tags=['install'])


@router.get('/status', response_model=InstallStatus)
def install_status():
  installed_state = load_install_state()
  installed = bool(installed_state.get('installed')) if isinstance(installed_state, dict) else False
  connected = installer_service.test_mysql_connection(settings.database_url)
  message = '数据库已连接' if connected else '尚未连接到数据库，需执行安装向导。'
  return {'connected': connected, 'installed': installed, 'message': message}


@router.post('/database/test', response_model=MysqlConnectionTestResult)
def install_test_database(payload: MysqlConnectionTestRequest):
  url = f"mysql+pymysql://root:{payload.root_password}@{payload.host}:{payload.port}"
  engine = create_engine(url)

  try:
    with engine.connect() as conn:
      conn.execute(text('SELECT 1'))
    return MysqlConnectionTestResult(success=True, error=None)
  except Exception as exc:  # noqa: BLE001
    return MysqlConnectionTestResult(success=False, error=str(exc))


@router.post('/run', response_model=InstallResult)
def run_install(payload: InstallRequest):
  try:
    result = installer_service.run_installation(payload)
    return result
  except HTTPException:
    raise
  except PermissionError as exc:  # noqa: PERF203
    raise HTTPException(status_code=400, detail='文件或目录权限不足，请确认写入权限。') from exc
  except Exception as exc:  # noqa: BLE001
    raise HTTPException(status_code=500, detail=f'安装失败：{exc}') from exc
