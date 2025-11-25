"""Database initialization helpers for schema creation and seed loading."""

from __future__ import annotations

from typing import Any, Dict

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.installer import seeder


def create_schema(engine: Engine) -> sessionmaker:
  """Create all tables and return a configured ``sessionmaker``."""

  Base.metadata.create_all(bind=engine)
  inspector = inspect(engine)
  columns = [col['name'] for col in inspector.get_columns('users')]
  if 'phone' not in columns:
    with engine.connect() as conn:
      conn.execute(text('ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL AFTER username'))
      conn.execute(text('CREATE UNIQUE INDEX idx_users_phone ON users (phone)'))
      conn.execute(text('UPDATE users SET phone = username WHERE phone IS NULL OR phone = ""'))
      conn.commit()
  return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def seed_all(
    db: Session,
    *,
    admin_payload: Dict[str, str],
    settings_overrides: Dict[str, Any],
    integrations: Dict[str, Dict[str, Any]],
    overwrite_existing: bool = True,
) -> None:
  """Seed all predefined data sets into the database."""

  seeder.seed_products(db)
  seeder.seed_users(db, admin_payload)
  seeder.seed_admin_users(db, overwrite_existing=overwrite_existing)
  seeder.seed_settings(db, settings_overrides, overwrite_existing=overwrite_existing)
  seeder.seed_integrations(
    db,
    integrations.get('wechat', {}),
    integrations.get('sms', {}),
    overwrite_existing=overwrite_existing,
  )
  seeder.seed_membership_settings(db, overwrite_existing=overwrite_existing)
  seeder.seed_recharge_records(db, overwrite_existing=overwrite_existing)
  seeder.seed_dashboard_stats(db, overwrite_existing=overwrite_existing)
  seeder.seed_admin_orders(db, overwrite_existing=overwrite_existing)
  seeder.seed_courses(db, overwrite_existing=overwrite_existing)
