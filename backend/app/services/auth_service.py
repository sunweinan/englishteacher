from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.database import get_db

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


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
  user = db.query(User).filter(User.username == username).first()
  if user is None:
    raise HTTPException(status_code=401, detail='User not found')
  return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
  if current_user.role != 'admin':
    raise HTTPException(status_code=403, detail='Not enough permissions')
  return current_user
