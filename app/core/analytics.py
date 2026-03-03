"""analytics.py

This file contains streak logic.
No database code here..
"""

from datetime import datetime, timedelta, date


def _parse_iso(text):
    text = text.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def filter_habits_by_periodicity(habits, periodicity):
    """Return only daily OR weekly habits."""
    result = []
    for h in habits:
        if h.periodicity == periodicity:
            result.append(h)
    return result


def _unique_days(checkoffs):
    days = set()
    for c in checkoffs:
        days.add(_parse_iso(c["completed_at"]).date())
    return sorted(list(days))


def _unique_weeks(checkoffs):
    weeks = set()
    for c in checkoffs:
        iso = _parse_iso(c["completed_at"]).isocalendar()
        weeks.add((iso.year, iso.week))
    return sorted(list(weeks))


def _longest_days(days):
    if not days:
        return 0

    best = 1
    current = 1

    for i in range(1, len(days)):
        if days[i] == days[i - 1] + timedelta(days=1):
            current += 1
        else:
            if current > best:
                best = current
            current = 1

    if current > best:
        best = current

    return best


def _next_week(year, week):
    monday = date.fromisocalendar(year, week, 1)
    monday2 = monday + timedelta(days=7)
    iso = monday2.isocalendar()
    return (iso.year, iso.week)


def _longest_weeks(weeks):
    if not weeks:
        return 0

    best = 1
    current = 1

    for i in range(1, len(weeks)):
        prev = weeks[i - 1]
        expected = _next_week(prev[0], prev[1])

        if weeks[i] == expected:
            current += 1
        else:
            if current > best:
                best = current
            current = 1

    if current > best:
        best = current

    return best


def longest_streak_for_habit(habit, habit_checkoffs):
    """Return longest streak for a habit object."""
    if habit.periodicity == "daily":
        return _longest_days(_unique_days(habit_checkoffs))

    if habit.periodicity == "weekly":
        return _longest_weeks(_unique_weeks(habit_checkoffs))

    return 0


def longest_streak_across_all_habits(habits, all_checkoffs):
    """Return (best_habit, best_streak)."""
    best_habit = None
    best_streak = 0

    grouped = {}
    for c in all_checkoffs:
        hid = c["habit_id"]
        if hid not in grouped:
            grouped[hid] = []
        grouped[hid].append(c)

    for h in habits:
        streak = longest_streak_for_habit(h, grouped.get(h.id, []))
        if streak > best_streak:
            best_streak = streak
            best_habit = h

    return best_habit, best_streak
