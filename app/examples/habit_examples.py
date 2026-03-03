"""habit_examples.py

This file adds demo habits and demo checkoffs automatically every run
It refreshes the last 28 days and avoids duplicates by deleting old demo checkoffs first.
"""

from datetime import datetime, timedelta

from app.db import storage
from datetime import datetime, timedelta



EXAMPLE_HABITS = [
    ("Go Running", "Go for a 20 minute run", "daily"),
    ("Workout", "Do a 30 minute workout", "daily"),
    ("Take Lectures and Study", "Attend lectures and study for 1 hour", "daily"),
    ("Do Grocery Shopping", "Buy groceries for the week", "weekly"),
    ("Call Parents", "Call parents once a week", "weekly"),
]


def _iso(dt):
    return dt.replace(microsecond=0).isoformat(sep=" ")


def ensure_example_data(conn):
    now = datetime.now().replace(microsecond=0)
    today = now.date()

    start_day = today - timedelta(days=27)

    start_dt = datetime(start_day.year, start_day.month, start_day.day, 0, 0, 0)
    end_dt = datetime(today.year, today.month, today.day, 23, 59, 59)

    start_iso = _iso(start_dt)
    end_iso = _iso(end_dt)

    # 1) Make sure example habits exist
    habit_ids = {}

    for name, task, periodicity in EXAMPLE_HABITS:
        existing = storage.get_example_habit_by_name(conn, name)
        if existing:
            habit_ids[name] = existing.id
        else:
            habit_ids[name] = storage.add_habit(conn, name, task, periodicity, _iso(now), is_example=1)

    
    
    # 2) Refresh checkoffs for each example habit
    for name, task, periodicity in EXAMPLE_HABITS:
        hid = habit_ids[name]

        storage.delete_example_checkoffs_between(conn, hid, start_iso, end_iso)

        if periodicity == "daily":
            _add_daily_checkoffs(conn, hid, start_day, today)
        else:
            _add_weekly_checkoffs(conn, hid, today)


def _add_daily_checkoffs(conn, habit_id, start_day, end_day):
    current = start_day
    counter = 0

    while current <= end_day:
        counter += 1
        hour = 8 if counter % 2 == 0 else 19
        completed = datetime(current.year, current.month, current.day, hour, 15, 0)
        storage.add_checkoff(conn, habit_id, _iso(completed), is_example=1)
        current = current + timedelta(days=1)


def _add_weekly_checkoffs(conn, habit_id, today):
    monday_this_week = today - timedelta(days=today.weekday())

    for i in range(4):
        monday = monday_this_week - timedelta(days=7 * (3 - i))
        completed = datetime(monday.year, monday.month, monday.day, 8, 0, 0)
        storage.add_checkoff(conn, habit_id, _iso(completed), is_example=1)
