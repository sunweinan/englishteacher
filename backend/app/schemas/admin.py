from pydantic import BaseModel, Field, field_validator


class DatabaseTestRequest(BaseModel):
  host: str = Field(..., description='MySQL server host or IP')
  port: int = Field(3306, ge=1, le=65535, description='MySQL port')
  db_name: str = Field(..., description='Target database name')
  db_user: str = Field(..., description='Application database user')
  db_password: str = Field(..., description='Application database password')
  root_password: str = Field(..., description='Default root password to verify')

  @field_validator('host', 'db_name', 'db_user', 'db_password', 'root_password')
  @classmethod
  def _not_blank(cls, value: str) -> str:
    if not str(value).strip():
      raise ValueError('字段不能为空')
    return value


class DatabaseTestResult(BaseModel):
  root_connected: bool
  database_exists: bool
  database_authenticated: bool
  message: str
