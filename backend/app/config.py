import os
from typing import Any, Dict

from pydantic import BaseModel


def _default_wechat_pay_config() -> Dict[str, Any]:
  site_cfg = _default_site_config()
  return {
    'app_id': os.getenv('WECHAT_PAY_APP_ID', 'wechat-app-id'),
    'mch_id': os.getenv('WECHAT_PAY_MCH_ID', 'wechat-mch-id'),
    'api_key': os.getenv('WECHAT_PAY_API_KEY', 'replace-with-api-key'),
    'notify_url': os.getenv('WECHAT_PAY_NOTIFY_URL', f"https://{site_cfg.get('domain', 'localhost')}/api/payments/wechat/notify"),
  }


def _default_database_config() -> Dict[str, Any]:
  return {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Ad123456'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'name': os.getenv('DB_NAME', 'englishteacher'),
  }


def _default_site_config() -> Dict[str, Any]:
  return {
    'ip': os.getenv('SITE_IP', '127.0.0.1'),
    'domain': os.getenv('SITE_DOMAIN', 'localhost'),
  }


def _build_database_url(config: Dict[str, Any]) -> str:
  if os.getenv('DATABASE_URL'):
    return os.getenv('DATABASE_URL')

  db_cfg = {**_default_database_config(), **config.get('database', {})}
  user = db_cfg.get('user')
  password = db_cfg.get('password')
  host = db_cfg.get('host')
  port = db_cfg.get('port')
  name = db_cfg.get('name')
  return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"


def _cors_origins_from_env() -> list[str]:
  value = os.getenv('CORS_ORIGINS')
  if not value:
    return ['*']
  return [origin.strip() for origin in value.split(',') if origin.strip()]


class WechatPaySettings(BaseModel):
  app_id: str
  mch_id: str
  api_key: str
  notify_url: str


class Settings(BaseModel):
  database_url: str
  jwt_secret: str = os.getenv('JWT_SECRET', 'supersecret')
  jwt_algorithm: str = 'HS256'
  access_token_expire_minutes: int = 60 * 24
  cors_origins: list[str]
  site_ip: str
  site_domain: str
  wechat_pay: WechatPaySettings


_default_config = {
  'database': _default_database_config(),
  'site': _default_site_config(),
  'wechat_pay': _default_wechat_pay_config(),
}
settings = Settings(
  database_url=_build_database_url(_default_config),
  cors_origins=_cors_origins_from_env(),
  site_ip=_default_config.get('site', {}).get('ip', '127.0.0.1'),
  site_domain=_default_config.get('site', {}).get('domain', 'localhost'),
  wechat_pay=WechatPaySettings(**_default_config.get('wechat_pay', {}))
)
