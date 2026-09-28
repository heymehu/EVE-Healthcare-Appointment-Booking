from collections.abc import Generator

from sqlalchemy import Boolean, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {}
engine_kwargs: dict = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if ":memory:" in settings.DATABASE_URL:
        engine_kwargs["poolclass"] = StaticPool
        engine_kwargs.pop("pool_pre_ping", None)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema() -> None:
    """Add columns introduced after a database was first created.

    create_all() never alters existing tables, so older SQLite files keep their
    original column set and every query against a new column fails. This walks
    the metadata and issues an idempotent ADD COLUMN for anything missing.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            present = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in present:
                    continue
                ddl = column.type.compile(engine.dialect)
                statement = f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {ddl}'
                if not column.nullable and column.default is None and column.server_default is None:
                    literal = "0" if isinstance(column.type, Boolean) else "''"
                    statement += f" NOT NULL DEFAULT {literal}"
                connection.execute(text(statement))
