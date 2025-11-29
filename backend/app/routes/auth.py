from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import LoginResponse, Token, LoginRequest, SendCodeRequest, PhoneLoginRequest
from app.schemas.user import UserOut, UserCreate
from app.services import auth_service
from app.core.database import get_db

router = APIRouter()


@router.post('/login', response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
  user = auth_service.authenticate_user(db, payload.username, payload.password)
  token = auth_service.create_access_token(auth_service.build_token_payload(user))
  return {'access_token': token, 'token_type': 'bearer'}


@router.post('/send-code')
def send_code(payload: SendCodeRequest):
  code = auth_service.send_verification_code(payload.phone)
  return {'message': '验证码已发送', 'code': code}


@router.post('/code-login', response_model=LoginResponse)
def code_login(payload: PhoneLoginRequest, db: Session = Depends(get_db)):
  user, newly_registered = auth_service.login_with_phone_code(db, payload.phone, payload.code)
  token = auth_service.create_access_token(auth_service.build_token_payload(user))
  return {
    'access_token': token,
    'token_type': 'bearer',
    'user': user,
    'newly_registered': newly_registered
  }


@router.post('/admin/login', response_model=Token)
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
  user, is_default_admin = auth_service.admin_login(db, payload.username, payload.password)
  token = auth_service.create_access_token(auth_service.build_token_payload(user))
  return {'access_token': token, 'token_type': 'bearer', 'is_default_admin': is_default_admin}


@router.post('/register', response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
  user = auth_service.register_user(db, payload)
  return user


@router.get('/me', response_model=UserOut)
def me(current_user=Depends(auth_service.get_current_user)):
  return current_user
