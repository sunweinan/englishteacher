"""安装向导相关的状态文件读写工具。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

INSTALL_STATE_PATH = Path(__file__).resolve().parent.parent / 'state' / 'installation.json'
SERVER_CONFIG_PATH = INSTALL_STATE_PATH.parent / 'server.json'
INSTALL_PERMISSION_COMMAND = 'chmod -R 775 backend/app/state'
INSTALL_STATE_DIR = INSTALL_STATE_PATH.parent


def ensure_install_state_dir() -> None:
  """确保安装状态目录存在。"""

  INSTALL_STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_install_state() -> Dict[str, Any]:
  """读取安装状态文件，异常或缺失时返回空字典。"""

  try:
    if INSTALL_STATE_PATH.exists():
      with INSTALL_STATE_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)
  except Exception:
    return {}
  return {}


def load_server_config() -> Dict[str, Any]:
  """读取服务器配置文件，异常时安全返回空字典。"""

  try:
    if SERVER_CONFIG_PATH.exists():
      with SERVER_CONFIG_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)
  except Exception:
    return {}
  return {}


def save_install_state(state: Dict[str, Any]) -> None:
  """将最新的安装状态写回磁盘。"""

  ensure_install_state_dir()
  with INSTALL_STATE_PATH.open('w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)


def save_server_config(config: Dict[str, Any]) -> None:
  """持久化服务器配置（如 IP、端口）。"""

  ensure_install_state_dir()
  with SERVER_CONFIG_PATH.open('w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)


def update_install_state(config_updates: Dict[str, Any]) -> Dict[str, Any]:
  """合并部分配置变更到安装状态，并立即保存。"""

  state = load_install_state()
  if not isinstance(state, dict):
    state = {}

  existing_config: Dict[str, Any] = state.get('config', {}) if isinstance(state.get('config'), dict) else {}

  def _merge_section(section: str, values: Dict[str, Any]) -> Dict[str, Any]:
    """更新指定配置段，仅覆盖非空值。"""

    current = existing_config.get(section, {}) if isinstance(existing_config.get(section), dict) else {}
    current.update({k: v for k, v in values.items() if v is not None})
    return current

  if database := config_updates.get('database'):
    existing_config['database'] = _merge_section('database', database)
  if site := config_updates.get('site'):
    existing_config['site'] = _merge_section('site', site)

  state['config'] = existing_config
  save_install_state(state)
  return state
