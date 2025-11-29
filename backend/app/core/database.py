"""数据库初始化和 Session 管理工具。"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings


def _ensure_database_exists() -> None:
  """确保目标数据库存在，不存在时尝试创建。

  通过读取配置中的连接串拆分出数据库名与服务器地址，
  先连接到服务器级别再执行 `CREATE DATABASE` 语句，
  以便安装流程尚未运行时也能正常启动后续逻辑。
  """

  try:
    url = make_url(settings.database_url)
    database_name = url.database
    if not database_name:
      return

    server_url = url.set(database=None)
    server_engine = create_engine(server_url, echo=False, future=True, isolation_level='AUTOCOMMIT')
    with server_engine.connect() as connection:
      connection.execute(text(
        f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
      ))
  except Exception:
    # 在安装向导执行前允许无数据库环境启动
    return


_ensure_database_exists()
engine = create_engine(settings.database_url, echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db() -> Session:
  """FastAPI 依赖：提供请求级数据库会话，并在响应后关闭。"""

  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


def init_db():
  """导入模型并创建所有数据表。"""

  import app.models  # noqa: F401
  Base.metadata.create_all(bind=engine)
