from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

INSTALL_STATE_PATH = Path(__file__).resolve().parent.parent / 'install' / 'state' / 'installation.json'


def ensure_install_state_dir() -> None:
  INSTALL_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_install_state() -> Dict[str, Any]:
  try:
    if INSTALL_STATE_PATH.exists():
      with INSTALL_STATE_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)
  except Exception:
    return {}
  return {}


def save_install_state(state: Dict[str, Any]) -> None:
  ensure_install_state_dir()
  with INSTALL_STATE_PATH.open('w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
