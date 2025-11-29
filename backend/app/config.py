import os
from typing import Any, Dict

from pydantic import BaseModel

from app.core.config_store import load_config
from app.core.install_state import load_install_state


def _install_overrides() -> Dict[str, Any]:
  config = load_config()
  if isinstance(config, dict) and config:
    return config

  state = load_install_state()
  return state.get('config', {}) if isinstance(state, dict) else {}


_installed_config = _install_overrides()


def _get_env(keys: list[str], default: Any | None = None) -> Any:
  for key in keys:
    value = os.getenv(key)
    if value:
      return value
  return default


def _default_database_config() -> Dict[str, Any]:
  install_db = _installed_config.get('database', {}) if isinstance(_installed_config, dict) else {}
  return {
    # Prefer installer overrides, then DB_* variables, then MySQL container defaults
    'user': install_db.get('user') or _get_env(['DB_USER', 'MYSQL_USER'], 'user'),
    'password': install_db.get('password') or _get_env(['DB_PASSWORD', 'MYSQL_PASSWORD'], 'password'),
    'host': install_db.get('host') or _get_env(['DB_HOST', 'MYSQL_HOST'], 'db'),
    'port': int(install_db.get('port') or _get_env(['DB_PORT', 'MYSQL_PORT'], 3306)),
    'name': install_db.get('name') or _get_env(['DB_NAME', 'MYSQL_DATABASE'], 'englishteacher'),
  }


def _default_site_config() -> Dict[str, Any]:
  install_site = _installed_config.get('site', {}) if isinstance(_installed_config, dict) else {}
  return {
    'ip': install_site.get('ip', os.getenv('SITE_IP', '127.0.0.1')),
    'domain': install_site.get('domain', os.getenv('SITE_DOMAIN', 'localhost')),
    'backend_port': int(install_site.get('backend_port', os.getenv('SITE_PORT', 8001))),
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
  if not all([user, password, host, name]):
    raise ValueError('Database configuration is incomplete. Please set DATABASE_URL or DB_* environment variables.')
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
  site_port: int


_default_config = {
  'database': _default_database_config(),
  'site': _default_site_config(),
}
settings = Settings(
  database_url=_build_database_url(_default_config),
  cors_origins=_cors_origins_from_env(),
  site_ip=_default_config.get('site', {}).get('ip', '127.0.0.1'),
  site_domain=_default_config.get('site', {}).get('domain', 'localhost'),
  site_port=int(_default_config.get('site', {}).get('backend_port', 8001))
)
