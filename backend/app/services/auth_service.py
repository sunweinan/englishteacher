import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.database import get_db

DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'root')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'Ad123456')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def verify_password(plain_password: str, hashed_password: str) -> bool:
  try:
    return pwd_context.verify(plain_password, hashed_password)
  except ValueError:
    # Handle invalid or legacy hashes gracefully instead of bubbling up
    return False


def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _build_default_admin_user(role: str = 'admin') -> User:
  return User(id=0, username=DEFAULT_ADMIN_USERNAME, password_hash='', role=role)


def _ensure_admin_user(db: Session, username: str, password: str) -> User:
  existing = db.query(User).filter(User.username == username).first()
  if existing:
    return existing
  user = User(username=username, password_hash=get_password_hash(password), role='admin')
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


def admin_login(db: Session, username: str, password: str) -> tuple[User, bool]:
  """Authenticate admin; fallback to default credentials when DB unavailable."""
  db_error: SQLAlchemyError | None = None
  user: User | None = None
  try:
    user = db.query(User).filter(User.username == username).first()
  except SQLAlchemyError as exc:  # noqa: PERF203
    db_error = exc

  if user and verify_password(password, user.password_hash):
    return user, False

  is_default_credentials = username == DEFAULT_ADMIN_USERNAME and password == DEFAULT_ADMIN_PASSWORD
  if is_default_credentials:
    if db_error is None:
      user = _ensure_admin_user(db, username, password)
      return user, False
    return _build_default_admin_user(), True

  if db_error:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='数据库连接失败，请稍后重试') from db_error

  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')


def build_token_payload(user: User, *, is_default_admin: bool = False) -> dict:
  payload = {'sub': user.username, 'role': user.role}
  if is_default_admin:
    payload['is_default_admin'] = True
  return payload


def authenticate_user(db: Session, username: str, password: str) -> User:
  user = db.query(User).filter(User.username == username).first()
  if not user or not verify_password(password, user.password_hash):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
  return user


def register_user(db: Session, user_in: UserCreate) -> User:
  if db.query(User).filter(User.username == user_in.username).first():
    raise HTTPException(status_code=400, detail='Username already exists')
  user = User(username=user_in.username, password_hash=get_password_hash(user_in.password), role=user_in.role)
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
  try:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    username: str | None = payload.get('sub')
    role = payload.get('role', 'user')
    is_default_admin = payload.get('is_default_admin', False)
    if username is None:
      raise HTTPException(status_code=401, detail='Invalid token')
  except Exception as exc:  # noqa: BLE001
    raise HTTPException(status_code=401, detail='Invalid token') from exc
  db_error: Exception | None = None
  user: User | None = None
  try:
    user = db.query(User).filter(User.username == username).first()
  except Exception as exc:  # noqa: BLE001
    db_error = exc

  if user:
    return user

  if is_default_admin and username == DEFAULT_ADMIN_USERNAME:
    return _build_default_admin_user(role)

  if db_error:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Database unavailable') from db_error

  raise HTTPException(status_code=401, detail='User not found')


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
  if current_user.role != 'admin':
    raise HTTPException(status_code=403, detail='Not enough permissions')
  return current_user
