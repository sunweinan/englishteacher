from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.core.config_store import CONFIG_PATH as SERVER_CONFIG_PATH
from app.core.config_store import load_config, merge_config_updates, save_config

INSTALL_STATE_PATH = Path(__file__).resolve().parent.parent / 'state' / 'installation.json'
INSTALL_PERMISSION_COMMAND = 'chmod -R 775 backend/app/state'
INSTALL_STATE_DIR = INSTALL_STATE_PATH.parent


def ensure_install_state_dir() -> None:
  INSTALL_STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_install_state() -> Dict[str, Any]:
  try:
    if INSTALL_STATE_PATH.exists():
      with INSTALL_STATE_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)
  except Exception:
    return {}
  return {}


def load_server_config() -> Dict[str, Any]:
  return load_config()


def save_install_state(state: Dict[str, Any]) -> None:
  ensure_install_state_dir()
  with INSTALL_STATE_PATH.open('w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)


def save_server_config(config: Dict[str, Any]) -> None:
  save_config(config)


def update_install_state(config_updates: Dict[str, Any]) -> Dict[str, Any]:
  """Merge partial configuration into config.json and snapshot to installation.json."""

  merged_config = merge_config_updates(config_updates)
  state = load_install_state()
  if not isinstance(state, dict):
    state = {}

  state['config'] = merged_config
  save_install_state(state)
  return state
