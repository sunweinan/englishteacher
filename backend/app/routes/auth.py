"""认证相关路由：登录、注册、验证码等接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, PhoneLoginRequest, SendCodeRequest, Token
from app.schemas.user import UserCreate, UserOut
from app.services import auth_service

router = APIRouter()


@router.post('/login', response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
  """账号密码登录，返回访问令牌。"""

  user = auth_service.authenticate_user(db, payload.username, payload.password)
  token = auth_service.create_access_token(auth_service.build_token_payload(user))
  return {'access_token': token, 'token_type': 'bearer'}


@router.post('/send-code')
def send_code(payload: SendCodeRequest):
  """发送短信验证码，当前实现返回生成的验证码。"""

  code = auth_service.send_verification_code(payload.phone)
  return {'message': '验证码已发送', 'code': code}


@router.post('/code-login', response_model=LoginResponse)
def code_login(payload: PhoneLoginRequest, db: Session = Depends(get_db)):
  """使用手机验证码登录或注册用户。"""

  user = auth_service.login_with_phone_code(db, payload.phone, payload.code)
  token = auth_service.create_access_token(auth_service.build_token_payload(user))
  return {'access_token': token, 'token_type': 'bearer', 'user': user}


@router.post('/admin/login', response_model=Token)
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
  """管理员登录，支持数据库和安装默认账户。"""

  user, is_default_admin = auth_service.admin_login(db, payload.username, payload.password)
  token = auth_service.create_access_token(auth_service.build_token_payload(user))
  return {'access_token': token, 'token_type': 'bearer', 'is_default_admin': is_default_admin}


@router.post('/register', response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
  """注册新用户，返回创建后的用户信息。"""

  user = auth_service.register_user(db, payload)
  return user


@router.get('/me', response_model=UserOut)
def me(current_user=Depends(auth_service.get_current_user)):
  """获取当前登录用户信息。"""

  return current_user
