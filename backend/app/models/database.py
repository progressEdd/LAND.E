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
    """Create the database file directory if needed and run all migration SQL files in order."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Discover and sort all migration files (001_*.sql, 002_*.sql, etc.)
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        for migration_file in migration_files:
            migration_sql = migration_file.read_text()
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
