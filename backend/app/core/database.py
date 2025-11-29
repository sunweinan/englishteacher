from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings


def _ensure_database_exists() -> None:
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
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


def init_db():
  import app.models  # noqa: F401
  Base.metadata.create_all(bind=engine)
