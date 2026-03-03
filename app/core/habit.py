"""habit.py

I've made a Habit class to create objects with properties (e.g., habit.name, habit.periodicity), 
then added DailyHabit/WeeklyHabit via inheritance, made unit() behave differently through polymorphism, 
and kept checks like is_daily() inside the class for encapsulation.
"""


class Habit:
    """This class stores one habit's information (base class)."""

    def __init__(self, habit_id, name, task, periodicity, created_at, is_example=0, last_completed=None):
        self.id = habit_id
        self.name = name
        self.task = task
        self.periodicity = periodicity
        self.created_at = created_at
        self.is_example = is_example
        self.last_completed = last_completed

    # Encapsulation helpers
    def is_daily(self):
        return self.periodicity == "daily"

    def is_weekly(self):
        return self.periodicity == "weekly"

    # Polymorphism target method
    def unit(self):
        """Default unit if I call unit() on base Habit."""
        return "periods"


class DailyHabit(Habit):
    """Daily habit child class (inherits from Habit)."""

    def unit(self):
        return "days"


class WeeklyHabit(Habit):
    """Weekly habit child class (inherits from Habit)."""

    def unit(self):
        return "weeks"
