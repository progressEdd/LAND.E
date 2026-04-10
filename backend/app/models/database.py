"""SQLite schema creation and connection management with aiosqlite."""

import os
import re
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


def normalize_character_name(raw_name: str) -> str:
    """Extract canonical name from LLM-generated descriptive string.

    Examples:
        "Chloe Miller (teenage daughter)" -> "Chloe Miller"
        "The Weathervane (an inanimate object with unusual agency)" -> "Weathervane"
        "Dr. Sarah Chen" -> "Dr. Sarah Chen"
        "A mysterious stranger" -> "mysterious stranger"
    """
    # Remove parenthetical descriptions
    name = re.sub(r'\s*\([^)]*\)', '', raw_name).strip()
    # Remove leading articles
    name = re.sub(r'^(The|A|An)\s+', '', name, flags=re.IGNORECASE).strip()
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name)
    return name
