"""Database initialization helpers for schema creation and seed loading."""

from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.installer import seeder


def create_schema(engine: Engine) -> sessionmaker:
  """Create all tables and return a configured ``sessionmaker``."""

  Base.metadata.create_all(bind=engine)
  return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def seed_all(
    db: Session,
    *,
    admin_payload: Dict[str, str],
    settings_overrides: Dict[str, Any],
    integrations: Dict[str, Dict[str, Any]],
) -> None:
  """Seed all predefined data sets into the database."""

  seeder.seed_products(db)
  seeder.seed_users(db, admin_payload)
  seeder.seed_settings(db, settings_overrides)
  seeder.seed_integrations(db, integrations.get('wechat', {}), integrations.get('sms', {}))
  seeder.seed_membership_settings(db)
  seeder.seed_recharge_records(db)
  seeder.seed_dashboard_stats(db)
