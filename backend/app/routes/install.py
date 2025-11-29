from fastapi import APIRouter, HTTPException

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

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

  connected = False
  if settings.database_url:
    # 使用一次性 engine 检查当前配置的数据库连通性，避免影响全局数据库实例
    try:
      temp_engine = create_engine(settings.database_url)
      with temp_engine.connect() as conn:
        conn.execute(text('SELECT 1'))
      connected = True
    except Exception:  # noqa: BLE001
      connected = False

  message = '数据库已连接' if connected else '尚未连接到数据库，需执行安装向导。'
  return {'connected': connected, 'installed': installed, 'message': message}


@router.post('/database/test', response_model=MysqlConnectionTestResult)
def install_test_database(payload: MysqlConnectionTestRequest):
  url = f"mysql+pymysql://root:{payload.root_password}@{payload.host}:{payload.port}"
  engine = create_engine(url)

  try:
    with engine.connect() as conn:
      conn.execute(text('SELECT 1'))
    return MysqlConnectionTestResult(
      root_connected=True,
      database_exists=False,
      database_authenticated=False,
      message='已完成 root 连接验证，可继续创建业务数据库。'
    )
  except OperationalError as exc:  # noqa: PERF203
    message = '无法连接到 MySQL，请检查主机、端口或 root 密码。'
    if 'Access denied' in str(exc.orig):
      message = 'root 密码错误，无法连接 MySQL。'
    return MysqlConnectionTestResult(
      root_connected=False,
      database_exists=False,
      database_authenticated=False,
      message=message,
    )
  except Exception as exc:  # noqa: BLE001
    return MysqlConnectionTestResult(
      root_connected=False,
      database_exists=False,
      database_authenticated=False,
      message=str(exc)
    )


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
