"""SQLite schema creation and connection management with aiosqlite."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite


# Database file path (relative to backend/)
DB_DIR = Path("data")
DB_PATH = DB_DIR / "stories.db"

# Path to migration SQL
MIGRATIONS_DIR = Path(__file__).parent.parent / "db" / "migrations"


async def init_db() -> None:
    """Create the database file directory if needed and run migration SQL."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    migration_file = MIGRATIONS_DIR / "001_initial.sql"
    migration_sql = migration_file.read_text()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        await db.executescript(migration_sql)
        await db.commit()


@asynccontextmanager
async def get_db():
    """Async context manager that returns an aiosqlite connection with WAL mode enabled."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
    finally:
        await db.close()
