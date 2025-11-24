import pymysql
from fastapi import HTTPException, status
from pymysql.err import OperationalError

from app.schemas.admin import DatabaseTestRequest, DatabaseTestResult


def _connect(**kwargs):
  return pymysql.connect(connect_timeout=5, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, **kwargs)


def test_mysql_connection(payload: DatabaseTestRequest) -> DatabaseTestResult:
  required = [payload.host, payload.db_user, payload.db_name, payload.db_password]
  if any(not str(item).strip() for item in required):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='请先填写数据库的地址、账号、名称和密码后再检测。'
    )
  if not payload.root_password.strip():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='请填写默认 root 密码后再检测。')

  try:
    root_conn = _connect(host=payload.host, port=payload.port, user='root', password=payload.root_password)
    root_connected = True
  except OperationalError as exc:  # noqa: PERF203
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail='无法连接到 MySQL，请确认地址和默认 root 密码是否正确。'
    ) from exc

  database_exists = False
  try:
    with root_conn.cursor() as cursor:  # type: ignore[var-annotated]
      cursor.execute('SHOW DATABASES LIKE %s', (payload.db_name,))
      database_exists = cursor.fetchone() is not None
  finally:
    root_conn.close()  # type: ignore[var-annotated]

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

  return DatabaseTestResult(
    root_connected=root_connected,
    database_exists=database_exists,
    database_authenticated=database_authenticated,
    message=summary
  )
