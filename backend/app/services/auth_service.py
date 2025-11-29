"""用户认证与授权相关的业务逻辑。"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.core.install_state import load_install_state
from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=['pbkdf2_sha256', 'bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')
DEFAULT_MEMBERSHIP = 'free'
CODE_EXPIRES_MINUTES = 5
_code_store: Dict[str, Tuple[str, datetime]] = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """校验明文密码与哈希是否匹配，兼容异常或旧格式。"""

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
  """生成密码哈希。"""

  return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  """根据负载生成 JWT 访问令牌，可选自定义过期时间。"""

  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _load_default_admin() -> tuple[str | None, str | None]:
  """从安装配置中加载默认管理员账户。"""

  state = load_install_state()
  admin_config = state.get('admin') if isinstance(state, dict) else {}
  if isinstance(admin_config, dict):
    username = admin_config.get('username')
    password = admin_config.get('password')
    return str(username) if username else None, str(password) if password else None
  return None, None


def _build_fallback_admin(username: str, password: str) -> User:
  """当数据库不可用时构造临时管理员对象。"""

  return User(
    username=username,
    phone=None,
    password_hash=get_password_hash(password),
    role='admin',
    membership_level=DEFAULT_MEMBERSHIP,
    membership_expires_at=None
  )


def admin_login(db: Session, username: str, password: str) -> tuple[User, bool]:
  """管理员登录，返回用户对象及是否为默认账户标记。"""

  db_error: SQLAlchemyError | None = None
  user: User | None = None
  try:
    user = db.query(User).filter(User.username == username).first()
  except SQLAlchemyError as exc:  # noqa: PERF203
    db_error = exc

  if user and verify_password(password, user.password_hash):
    if user.role != 'admin':
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough permissions')
    return user, False

  if db_error:
    default_username, default_password = _load_default_admin()
    if default_username and default_password and username == default_username and password == default_password:
      return _build_fallback_admin(default_username, default_password), True
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='数据库连接失败，请稍后重试') from db_error

  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')


def build_token_payload(user: User) -> dict:
  """构建 JWT 负载，包含用户名与角色。"""

  return {'sub': user.username, 'role': user.role}


def authenticate_user(db: Session, username: str, password: str) -> User:
  """使用数据库校验普通用户登录。"""

  user = db.query(User).filter(User.username == username).first()
  if not user or not verify_password(password, user.password_hash):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
  return user


def send_verification_code(phone: str) -> str:
  """生成并暂存手机验证码，简单校验号码格式。"""

  if not phone.isdigit() or len(phone) < 4 or len(phone) > 20:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='手机号格式不正确')
  code = f"{secrets.randbelow(1000000):06d}"
  _code_store[phone] = (code, datetime.utcnow() + timedelta(minutes=CODE_EXPIRES_MINUTES))
  return code


def _ensure_code_valid(phone: str, code: str) -> None:
  """校验验证码是否存在、未过期且匹配。"""

  stored = _code_store.get(phone)
  if not stored:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='请先获取验证码')
  stored_code, expires_at = stored
  if datetime.utcnow() > expires_at:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='验证码已过期，请重新获取')
  if code != stored_code:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='验证码错误')


def login_with_phone_code(db: Session, phone: str, code: str) -> User:
  """使用验证码登录或注册用户，必要时创建新账户。"""

  _ensure_code_valid(phone, code)
  _code_store.pop(phone, None)
  db_error: SQLAlchemyError | None = None
  user: User | None = None
  try:
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
      user = User(
        username=phone,
        phone=phone,
        password_hash=get_password_hash(code),
        role='user',
        membership_level=DEFAULT_MEMBERSHIP,
        membership_expires_at=None
      )
      db.add(user)
      db.commit()
      db.refresh(user)
  except SQLAlchemyError as exc:  # noqa: PERF203
    db_error = exc

  if db_error:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='数据库连接失败，请稍后重试') from db_error

  if not user:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='无法创建或获取用户')

  return user


def register_user(db: Session, user_in: UserCreate) -> User:
  """注册新用户，包含会员有效期解析与唯一性校验。"""

  if db.query(User).filter(User.username == user_in.username).first():
    raise HTTPException(status_code=400, detail='Username already exists')
  phone = user_in.phone or user_in.username
  expires_at = None
  if isinstance(user_in.membership_expires_at, str):
    try:
      expires_at = datetime.fromisoformat(user_in.membership_expires_at)
    except ValueError:
      expires_at = None
  elif user_in.membership_expires_at:
    expires_at = user_in.membership_expires_at
  user = User(
    username=user_in.username,
    phone=phone,
    password_hash=get_password_hash(user_in.password),
    role=user_in.role,
    membership_level=user_in.membership_level,
    membership_expires_at=expires_at
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
  """解析 JWT 并返回当前用户，数据库不可用时返回 503。"""

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
