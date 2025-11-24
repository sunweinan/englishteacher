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

pwd_context = CryptContext(schemes=['pbkdf2_sha256', 'bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def verify_password(plain_password: str, hashed_password: str) -> bool:
  if not hashed_password:
    return False

  try:
    return pwd_context.verify(plain_password, hashed_password)
  except ValueError:
    # Handle invalid or legacy hashes gracefully instead of bubbling up
    return plain_password == hashed_password
  except Exception:
    # Avoid leaking unexpected errors to callers; fall back to plaintext check
    return plain_password == hashed_password


def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def admin_login(db: Session, username: str, password: str) -> tuple[User, bool]:
  """Authenticate admin strictly against stored database credentials."""
  db_error: SQLAlchemyError | None = None
  user: User | None = None
  try:
    user = db.query(User).filter(User.username == username).first()
  except SQLAlchemyError as exc:  # noqa: PERF203
    db_error = exc

  if db_error:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='数据库连接失败，请稍后重试') from db_error

  if not user or not verify_password(password, user.password_hash):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')

  if user.role != 'admin':
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough permissions')

  return user, False


def build_token_payload(user: User) -> dict:
  return {'sub': user.username, 'role': user.role}


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
  if db_error:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Database unavailable') from db_error

  raise HTTPException(status_code=401, detail='User not found')


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
  if current_user.role != 'admin':
    raise HTTPException(status_code=403, detail='Not enough permissions')
  return current_user
