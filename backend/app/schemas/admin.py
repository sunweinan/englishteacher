from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DatabaseTestRequest(BaseModel):
  host: str = Field(..., description='MySQL server host or IP')
  port: int = Field(3306, ge=1, le=65535, description='MySQL port')
  db_name: str | None = Field(None, description='Target database name')
  db_user: str | None = Field(None, description='Application database user')
  db_password: str | None = Field(None, description='Application database password')
  root_password: str = Field(..., description='Default root password to verify')

  @field_validator('host', 'root_password')
  @classmethod
  def _required_not_blank(cls, value: str) -> str:
    if not str(value).strip():
      raise ValueError('字段不能为空')
    return value

  @field_validator('db_name', 'db_user', 'db_password')
  @classmethod
  def _optional_not_blank(cls, value: str | None) -> str | None:
    if value is None:
      return value
    if not str(value).strip():
      raise ValueError('字段不能为空')
    return value


class DatabaseTestResult(BaseModel):
  root_connected: bool
  database_exists: bool
  database_authenticated: bool
  message: str


class SystemConfig(BaseModel):
  server_ip: str
  domain: str
  login_user: str
  login_password: str
  db_host: str
  db_port: int
  db_name: str
  db_user: str
  db_password: str
  root_password: str
  wechat_app_id: str | None = None
  wechat_mch_id: str | None = None
  wechat_api_key: str | None = None
  sms_provider: str | None = None
  sms_api_key: str | None = None
  sms_sign_name: str | None = None


class SystemConfigUpdate(SystemConfig):
  @field_validator('server_ip', 'domain', 'login_user', 'db_host', 'db_name', 'db_user', 'db_password', 'root_password')
  @classmethod
  def _not_blank(cls, value: str) -> str:
    if not str(value).strip():
      raise ValueError('字段不能为空')
    return value


class DashboardStat(BaseModel):
  label: str
  value: str
  note: str

  model_config = ConfigDict(from_attributes=True)


class AdminUserProfileOut(BaseModel):
  id: int
  nickname: str
  phone: str
  level: str
  register_at: datetime
  spend: float
  tests: int
  benefits: str
  recharges: list[str] = []
  note: str | None = None

  model_config = ConfigDict(from_attributes=True)


class AdminPaymentRecord(BaseModel):
  id: int
  user_display: str
  level: str
  amount: float
  channel: str
  order_no: str
  paid_at: datetime

  model_config = ConfigDict(from_attributes=True)


class AdminOrderItemOut(BaseModel):
  id: int
  name: str
  quantity: int
  price: float

  model_config = ConfigDict(from_attributes=True)


class AdminOrderOut(BaseModel):
  id: str
  user: str
  created_at: datetime
  status: str
  channel: str
  amount: float
  remark: str | None = None
  items: list[AdminOrderItemOut] = []

  model_config = ConfigDict(from_attributes=True)
