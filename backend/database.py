from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_legacy_schema():
    """Add small additive fields needed by newer local SQLite databases."""
    if not settings.database_url.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if "auth_users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("auth_users")}
    if "email" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE auth_users ADD COLUMN email VARCHAR(180)"))
            connection.execute(text("UPDATE auth_users SET email = username || '@legacy.invalid' WHERE email IS NULL"))
