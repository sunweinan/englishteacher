from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).resolve().parent.parent / 'state' / 'config.json'
LEGACY_SERVER_PATH = CONFIG_PATH.parent / 'server.json'


def _ensure_config_dir() -> None:
  CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path) -> Dict[str, Any]:
  try:
    if path.exists():
      with path.open('r', encoding='utf-8') as f:
        return json.load(f)
  except Exception:
    return {}
  return {}


def load_config() -> Dict[str, Any]:
  config = _load_json(CONFIG_PATH)
  if config:
    return config

  legacy = _load_json(LEGACY_SERVER_PATH)
  if legacy:
    try:
      save_config(legacy)
    except Exception:
      pass
    return legacy
  return {}


def save_config(config: Dict[str, Any]) -> None:
  _ensure_config_dir()
  with CONFIG_PATH.open('w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)


def merge_config_updates(updates: Dict[str, Any]) -> Dict[str, Any]:
  current = load_config()
  if not isinstance(current, dict):
    current = {}

  def _merge_section(name: str) -> None:
    base = current.get(name, {}) if isinstance(current.get(name), dict) else {}
    incoming = updates.get(name, {}) if isinstance(updates, dict) else {}
    if isinstance(incoming, dict):
      base.update({k: v for k, v in incoming.items() if v is not None})
    current[name] = base

  _merge_section('database')
  _merge_section('site')

  save_config(current)
  return current
