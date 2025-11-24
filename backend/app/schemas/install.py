from pydantic import BaseModel, Field


class MysqlConnectionConfig(BaseModel):
  host: str
  port: int = 3306
  root_password: str = Field(..., min_length=1)


class InstallStatus(BaseModel):
  connected: bool
  installed: bool
  message: str | None = None


class InstallRequest(BaseModel):
  server_domain: str
  server_ip: str
  backend_port: int = 8001
  mysql_url: str | None = None
  mysql_host: str | None = None
  mysql_port: int | None = 3306
  mysql_root_password: str
  database_name: str = 'enTeacher'
  database_user: str = 'admin'
  database_password: str = '123456'
  admin_username: str = 'root'
  admin_password: str = '123456'
  wechat_app_id: str | None = None
  wechat_mch_id: str | None = None
  wechat_api_key: str | None = None
  sms_provider: str | None = None
  sms_api_key: str | None = None
  sms_sign_name: str | None = None


class InstallStep(BaseModel):
  step: str
  label: str


class InstallResult(BaseModel):
  success: bool = True
  message: str
  next_url: str
  progress: list[InstallStep] | None = None
