import json
import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel


CONFIG_FILE = Path(__file__).with_name('app_settings.json')


def _load_file_config() -> Dict[str, Any]:
  if not CONFIG_FILE.exists():
    return {}

  with CONFIG_FILE.open() as f:
    try:
      return json.load(f)
    except json.JSONDecodeError:
      return {}


def _build_database_url(config: Dict[str, Any]) -> str:
  if os.getenv('DATABASE_URL'):
    return os.getenv('DATABASE_URL')

  db_cfg = config.get('database', {})
  user = db_cfg.get('user', 'user')
  password = db_cfg.get('password', 'password')
  host = db_cfg.get('host', 'localhost')
  port = db_cfg.get('port', 3306)
  name = db_cfg.get('name', 'englishteacher')
  return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"


def _cors_origins_from_env() -> list[str]:
  value = os.getenv('CORS_ORIGINS')
  if not value:
    return ['*']
  return [origin.strip() for origin in value.split(',') if origin.strip()]


class Settings(BaseModel):
  database_url: str
  jwt_secret: str = os.getenv('JWT_SECRET', 'supersecret')
  jwt_algorithm: str = 'HS256'
  access_token_expire_minutes: int = 60 * 24
  cors_origins: list[str]
  site_ip: str
  site_domain: str


_file_config = _load_file_config()
settings = Settings(
  database_url=_build_database_url(_file_config),
  cors_origins=_cors_origins_from_env(),
  site_ip=_file_config.get('site', {}).get('ip', '127.0.0.1'),
  site_domain=_file_config.get('site', {}).get('domain', 'localhost')
)
