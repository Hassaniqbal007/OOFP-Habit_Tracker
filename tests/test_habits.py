"""test_habits.py

Tests are done using unittest 

What does it tests you can see:
1) Analytics: filtering habits by daily/weekly
2) Analytics: longest streak for daily habit
3) Analytics: longest streak for weekly habit
4) Storage: insert habit + insert checkoff
5) Storage: cascade delete (delete habit also delete its checkoffs)
6) Storage: block duplicate checkoff in same day (daily habit)
"""

import os
import unittest
from datetime import datetime, timedelta


from app.db import storage
from app.core import analytics



def make_time_string(dt):
    """Make a clean timestamp string"""
    return dt.replace(microsecond=0).isoformat(sep=" ")


class TestAnalytics(unittest.TestCase):
    def test_filter_daily_habits(self):
        """I check that filtering by 'daily' returns only daily habits."""
        # I created fake Habit objects (same fields as Habit class)
        fake_habits = [
            type("H", (), {"periodicity": "daily"})(),
            type("H", (), {"periodicity": "weekly"})(),
            type("H", (), {"periodicity": "daily"})(),
        ]

        daily_only = analytics.filter_habits_by_periodicity(fake_habits, "daily")
        self.assertEqual(len(daily_only), 2)

    def test_daily_longest_streak(self):
        """I check daily streak = consecutive days."""
        # I make a fake habit object with periodicity=daily
        habit = type("H", (), {"periodicity": "daily"})()

        base = datetime(2026, 1, 1, 8, 0, 0)

        # 3 consecutive days, gap, then 2 days
        checkoffs = [
            {"habit_id": 1, "completed_at": make_time_string(base)},
            {"habit_id": 1, "completed_at": make_time_string(base + timedelta(days=1))},
            {"habit_id": 1, "completed_at": make_time_string(base + timedelta(days=2))},
            {"habit_id": 1, "completed_at": make_time_string(base + timedelta(days=4))},
            {"habit_id": 1, "completed_at": make_time_string(base + timedelta(days=5))},
        ]

        streak = analytics.longest_streak_for_habit(habit, checkoffs)
        self.assertEqual(streak, 3)

    def test_weekly_longest_streak(self):
        """I check weekly streak = consecutive ISO weeks."""
        habit = type("H", (), {"periodicity": "weekly"})()

        base = datetime(2026, 1, 1, 8, 0, 0)

        # 4 weeks in a row (7 day gap each)
        checkoffs = [
            {"habit_id": 1, "completed_at": make_time_string(base)},
            {"habit_id": 1, "completed_at": make_time_string(base + timedelta(days=7))},
            {"habit_id": 1, "completed_at": make_time_string(base + timedelta(days=14))},
            {"habit_id": 1, "completed_at": make_time_string(base + timedelta(days=21))},
        ]

        streak = analytics.longest_streak_for_habit(habit, checkoffs)
        self.assertEqual(streak, 4)


class TestStorage(unittest.TestCase):
    def setUp(self):
        """I create a fresh test database before each test."""
        self.test_db_name = "test_habits.db"

        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

        self.conn = storage.connect_db(self.test_db_name)
        storage.setup_db(self.conn)

    def tearDown(self):
        """I close and delete the test database after each test."""
        self.conn.close()

        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def test_insert_habit_and_checkoff(self):
        """I test inserting habit + inserting checkoff."""
        habit_id = storage.add_habit(
            self.conn,
            name="Test Habit",
            task="Do something",
            periodicity="daily",
            created_at="2026-01-01 10:00:00",
            is_example=0
        )
        self.assertTrue(habit_id > 0)

        checkoff_id = storage.add_checkoff(
            self.conn,
            habit_id=habit_id,
            completed_at="2026-01-01 12:00:00",
            is_example=0
        )
        self.assertTrue(checkoff_id > 0)

        checkoffs = storage.get_checkoffs(self.conn, habit_id)
        self.assertEqual(len(checkoffs), 1)

    def test_delete_habit_deletes_checkoffs(self):
        """I test cascade delete, deleting habit should also delete its checkoffs."""
        habit_id = storage.add_habit(
            self.conn,
            name="Cascade",
            task="Test",
            periodicity="daily",
            created_at="2026-01-01 00:00:00",
            is_example=0
        )

        storage.add_checkoff(self.conn, habit_id, "2026-01-01 08:00:00", 0)

        # Delete habit
        storage.remove_habit(self.conn, habit_id)

        # Checkoffs should also be gone
        all_checkoffs = storage.get_all_checkoffs(self.conn)
        self.assertEqual(len(all_checkoffs), 0)

    def test_block_duplicate_checkoff_same_day(self):
        """I test that daily habit cannot be checked off twice in same day make the habit tracker app more realistic."""
        habit_id = storage.add_habit(
            self.conn,
            name="No Duplicate",
            task="Test",
            periodicity="daily",
            created_at="2026-01-01 00:00:00",
            is_example=0
        )

        first = storage.add_checkoff(self.conn, habit_id, "2026-01-01 08:00:00", 0)
        second = storage.add_checkoff(self.conn, habit_id, "2026-01-01 20:00:00", 0)

        self.assertTrue(first > 0)
        self.assertEqual(second, -1)


if __name__ == "__main__":
    unittest.main()
