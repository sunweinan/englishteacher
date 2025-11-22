from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config import settings

engine = create_engine(settings.database_url, echo=False, future=True)
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
