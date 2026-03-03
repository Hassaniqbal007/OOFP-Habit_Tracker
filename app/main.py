"""main.py

This is my main CLI program.
I keep it simple:
show menu
take input
call storage + analytics
"""

from datetime import datetime

from app.db import storage
from app.core import analytics
from app.examples.habit_examples import ensure_example_data


def now_iso():
    """Return current timestamp in my DB format."""
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def pretty_time(text):
    """Make timestamp readable."""
    try:
        text = text.replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return text


def print_line():
    print("-" * 90)


def show_habits(conn):
    habits = storage.get_all_habits(conn)

    if not habits:
        print("No habits yet.")
        return

    print_line()
    print("Your Habits:")
    print_line()
    print(f"{'ID':<3} | {'Name':<18} | {'Type':<6} | {'Last Completed':<19} | {'Task'}")
    print_line()

    for h in habits:
        last = "Never"
        if h.last_completed:
            last = pretty_time(h.last_completed)

        name = h.name if len(h.name) <= 18 else h.name[:15] + "..."
        task = h.task if len(h.task) <= 40 else h.task[:37] + "..."

        print(f"{h.id:<3} | {name:<18} | {h.periodicity:<6} | {last:<19} | {task}")

    print_line()


def ask_habit_id(conn):
    show_habits(conn)
    try:
        habit_id = int(input("Enter habit ID: ").strip())
    except ValueError:
        print("Not a valid number.")
        return None

    if storage.get_habit(conn, habit_id) is None:
        print("Habit not found.")
        return None

    return habit_id


def create_habit(conn):
    name = input("Habit name: ").strip()
    if not name:
        print("Name is required.")
        return

    task = input("Habit task: ").strip()
    if not task:
        print("Task is required.")
        return

    periodicity = input("daily or weekly: ").strip().lower()
    if periodicity not in ("daily", "weekly"):
        print("Type daily or weekly.")
        return

    created_at = now_iso()
    storage.add_habit(conn, name, task, periodicity, created_at, is_example=0)
    print("Habit added!")


def delete_habit(conn):
    habit_id = ask_habit_id(conn)
    if habit_id is None:
        return

    habit = storage.get_habit(conn, habit_id)
    confirm = input(f"Delete '{habit.name}'? (yes/no): ").strip().lower()

    if confirm in ("yes", "y"):
        storage.remove_habit(conn, habit_id)
        print("Habit deleted.")
    else:
        print("Cancelled.")


def mark_completed(conn):
    habit_id = ask_habit_id(conn)
    if habit_id is None:
        return

    timestamp = now_iso()
    result = storage.add_checkoff(conn, habit_id, timestamp, is_example=0)
    habit = storage.get_habit(conn, habit_id)

    if result == -1:
        # Using encapsulation (is_daily)
        when = "today" if habit.is_daily() else "this week"
        print(f"You already completed it {when}.")
    else:
        print(f"Completed '{habit.name}' at {pretty_time(timestamp)}")


def show_history(conn):
    habit_id = ask_habit_id(conn)
    if habit_id is None:
        return

    habit = storage.get_habit(conn, habit_id)
    checkoffs = storage.get_checkoffs(conn, habit_id)

    print_line()
    print("History for:", habit.name)
    print_line()

    if not checkoffs:
        print("No completions yet.")
        return

    for c in checkoffs:
        print("✓", pretty_time(c["completed_at"]))

    print_line()


def show_habits_by_type(conn):
    periodicity = input("daily or weekly: ").strip().lower()
    if periodicity not in ("daily", "weekly"):
        print("Type daily or weekly.")
        return

    habits = storage.get_all_habits(conn)
    filtered = analytics.filter_habits_by_periodicity(habits, periodicity)

    if not filtered:
        print("No habits found.")
        return

    print_line()
    print(periodicity.upper(), "habits:")
    print_line()
    for h in filtered:
        print(f"{h.id}. {h.name} - {h.task}")
    print_line()


def show_best_streak(conn):
    habits = storage.get_all_habits(conn)
    checkoffs = storage.get_all_checkoffs(conn)

    best_habit, best_streak = analytics.longest_streak_across_all_habits(habits, checkoffs)

    if best_habit is None:
        print("No streaks yet.")
        return

    # Polymorphism: DailyHabit.unit() or WeeklyHabit.unit()
    unit = best_habit.unit()
    print(f"Best streak: {best_streak} {unit} for {best_habit.name}")


def show_one_habit_streak(conn):
    habit_id = ask_habit_id(conn)
    if habit_id is None:
        return

    habit = storage.get_habit(conn, habit_id)
    checkoffs = storage.get_checkoffs(conn, habit_id)

    streak = analytics.longest_streak_for_habit(habit, checkoffs)

    # Polymorphism again
    unit = habit.unit()
    print(f"Longest streak for {habit.name}: {streak} {unit}")


def run_app():
    conn = storage.connect_db()
    storage.setup_db(conn)

    ensure_example_data(conn)

    while True:
        print("\n--- Habit Tracker Menu ---")
        print("1) Show all habits")
        print("2) Create habit")
        print("3) Delete habit")
        print("4) Mark completed")
        print("5) Show history")
        print("6) Show daily/weekly habits")
        print("7) Show best streak")
        print("8) Show streak for one habit")
        print("0) Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            show_habits(conn)
        elif choice == "2":
            create_habit(conn)
        elif choice == "3":
            delete_habit(conn)
        elif choice == "4":
            mark_completed(conn)
        elif choice == "5":
            show_history(conn)
        elif choice == "6":
            show_habits_by_type(conn)
        elif choice == "7":
            show_best_streak(conn)
        elif choice == "8":
            show_one_habit_streak(conn)
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice.")

        input("Press Enter to continue...")

    conn.close()


if __name__ == "__main__":
    run_app()


