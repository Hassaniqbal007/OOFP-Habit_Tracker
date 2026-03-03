"""storage.py

This file contains all database (SQLite) code.
I keep SQL here so my main program stays clean.

SQLite cascade deletes work only if you enable foreign keys
"""

import sqlite3
from datetime import datetime

from app.core.habit import Habit, DailyHabit, WeeklyHabit


DB_FILE = "habits.db"


def connect_db(db_path=DB_FILE):
    """Open database connection and enable foreign keys."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def setup_db(conn):
    """Create tables if they don't exist."""
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL CHECK(periodicity IN ('daily', 'weekly')),
            created_at TEXT NOT NULL,
            is_example INTEGER NOT NULL DEFAULT 0
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS checkoffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            is_example INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        );
    """)

    conn.commit()


# HABITS

def add_habit(conn, name, task, periodicity, created_at, is_example=0):
    """Insert a habit and return its id."""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habits (name, task, periodicity, created_at, is_example) VALUES (?, ?, ?, ?, ?)",
        (name, task, periodicity, created_at, is_example),
    )
    conn.commit()
    return int(cur.lastrowid)


def remove_habit(conn, habit_id):
    """Delete habit (its checkoffs delete automatically because of cascade)."""
    cur = conn.cursor()
    cur.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()


def _make_habit_object(row, last_completed_value=None):
    """Create the right Habit object (DailyHabit or WeeklyHabit)."""
    if row["periodicity"] == "daily":
        habit_obj = DailyHabit(
            row["id"],
            row["name"],
            row["task"],
            row["periodicity"],
            row["created_at"],
            row["is_example"],
            last_completed_value
        )
    else:
        habit_obj = WeeklyHabit(
            row["id"],
            row["name"],
            row["task"],
            row["periodicity"],
            row["created_at"],
            row["is_example"],
            last_completed_value
        )
    return habit_obj


def get_habit(conn, habit_id):
    """Get one habit object (or None)."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
    row = cur.fetchone()

    if not row:
        return None

    return _make_habit_object(row, None)


def get_all_habits(conn):
    """Get all habits (as Habit objects), also include last_completed."""
    cur = conn.cursor()
    cur.execute("""
        SELECT h.*, MAX(c.completed_at) AS last_completed
        FROM habits h
        LEFT JOIN checkoffs c ON h.id = c.habit_id
        GROUP BY h.id
        ORDER BY h.id
    """)

    habits = []
    for r in cur.fetchall():
        habits.append(_make_habit_object(r, r["last_completed"]))
    return habits


def get_example_habit_by_name(conn, name):
    """Find example habit (is_example=1) by name."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM habits WHERE name = ? AND is_example = 1", (name,))
    row = cur.fetchone()

    if not row:
        return None

    return _make_habit_object(row, None)





# CHECKOFFS 

def _parse_iso(text):
    """Convert timestamp string into datetime."""
    text = text.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def _period_key(periodicity, completed_at):
    """Return a key for duplicates:
    daily: YYYY-MM-DD
    weekly: ISO YEAR + ISO WEEK
    """
    dt = _parse_iso(completed_at)

    if periodicity == "daily":
        return dt.date().isoformat()

    iso = dt.isocalendar()
    return str(iso.year) + "-" + str(iso.week)


def _already_done_in_same_period(conn, habit_id, periodicity, completed_at, is_example):
    """Return True if a checkoff already exists in same day/week."""
    new_key = _period_key(periodicity, completed_at)

    cur = conn.cursor()
    cur.execute(
        "SELECT completed_at FROM checkoffs WHERE habit_id = ? AND is_example = ?",
        (habit_id, is_example),
    )

    for r in cur.fetchall():
        old_key = _period_key(periodicity, r["completed_at"])
        if old_key == new_key:
            return True

    return False


def add_checkoff(conn, habit_id, completed_at, is_example=0):
    """Insert checkoff.
    Returns:
    new checkoff id if inserted
    -1 if duplicate in same day/week
    """
    habit = get_habit(conn, habit_id)
    if habit is None:
        raise ValueError("Habit not found.")

    if _already_done_in_same_period(conn, habit_id, habit.periodicity, completed_at, is_example):
        return -1

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO checkoffs (habit_id, completed_at, is_example) VALUES (?, ?, ?)",
        (habit_id, completed_at, is_example),
    )
    conn.commit()
    return int(cur.lastrowid)


def get_checkoffs(conn, habit_id):
    """Return list of checkoffs for a habit (dicts)."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM checkoffs WHERE habit_id = ? ORDER BY completed_at", (habit_id,))
    return [dict(r) for r in cur.fetchall()]


def get_all_checkoffs(conn):
    """Return list of all checkoffs (dicts)."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM checkoffs ORDER BY completed_at")
    return [dict(r) for r in cur.fetchall()]


def delete_example_checkoffs_between(conn, habit_id, start_iso, end_iso):
    """Delete example checkoffs in a time window."""
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM checkoffs
        WHERE habit_id = ?
          AND is_example = 1
          AND completed_at >= ?
          AND completed_at <= ?
    """, (habit_id, start_iso, end_iso))
    conn.commit()
