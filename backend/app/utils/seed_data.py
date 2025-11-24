from __future__ import annotations

"""Helpers for persisting configuration back to seed data files."""

import json
from pathlib import Path
from typing import Any, Dict, List

SEED_DATA_DIR = Path(__file__).resolve().parent.parent / 'install' / 'seed_data'
SYSTEM_SETTINGS_FILE = SEED_DATA_DIR / 'system_settings.json'
SYSTEM_CONFIG_FILE = SEED_DATA_DIR / 'system_config.json'
PERMISSION_COMMAND = 'chmod -R 775 backend/app/install/seed_data'


def _load_json(path: Path, default: Any) -> Any:
  if not path.exists():
    return default
  with path.open('r', encoding='utf-8') as file:
    return json.load(file)


def _write_json(path: Path, data: Any) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open('w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=2)


def _settings_entries_to_map(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
  settings: Dict[str, Any] = {}
  for entry in entries:
    category = entry.get('category')
    key = entry.get('key')
    if category == 'site' and key:
      settings[key] = entry.get('value')
  return settings


def _upsert_setting(entries: List[Dict[str, Any]], category: str, key: str, value: Any, description: str) -> None:
  for entry in entries:
    if entry.get('category') == category and entry.get('key') == key:
      entry['value'] = '' if value is None else str(value)
      if description:
        entry['description'] = description
      return

  entries.append({
    'category': category,
    'key': key,
    'value': '' if value is None else str(value),
    'description': description
  })


def load_seed_config(default: Dict[str, Any] | None = None) -> Dict[str, Any]:
  """Load the latest seed configuration from disk.

  The values come from ``system_config.json`` and ``system_settings.json``. Missing
  fields fall back to the provided ``default`` dictionary.
  """

  defaults = default or {}
  seed_config: Dict[str, Any] = _load_json(SYSTEM_CONFIG_FILE, {})
  settings_entries: List[Dict[str, Any]] = _load_json(SYSTEM_SETTINGS_FILE, [])
  site_settings = _settings_entries_to_map(settings_entries)

  merged: Dict[str, Any] = {**defaults, **seed_config}
  if 'server_ip' not in merged and 'ip' in site_settings:
    merged['server_ip'] = site_settings['ip']
  if 'domain' not in merged and 'domain' in site_settings:
    merged['domain'] = site_settings['domain']

  return merged


def persist_seed_config(config: Dict[str, Any], *, backend_port: int) -> None:
  """Persist system configuration into the seed_data directory."""

  settings_entries: List[Dict[str, Any]] = _load_json(SYSTEM_SETTINGS_FILE, [])
  _upsert_setting(settings_entries, 'site', 'domain', config.get('domain'), '服务器域名')
  _upsert_setting(settings_entries, 'site', 'ip', config.get('server_ip'), '服务器IP')
  _upsert_setting(settings_entries, 'site', 'backend_port', backend_port, '后端服务端口')

  _write_json(SYSTEM_SETTINGS_FILE, settings_entries)

  _write_json(SYSTEM_CONFIG_FILE, {
    'server_ip': config.get('server_ip'),
    'domain': config.get('domain'),
    'login_user': config.get('login_user'),
    'login_password': config.get('login_password'),
    'db_host': config.get('db_host'),
    'db_port': config.get('db_port'),
    'db_name': config.get('db_name'),
    'db_user': config.get('db_user'),
    'db_password': config.get('db_password'),
    'root_password': config.get('root_password'),
  })
