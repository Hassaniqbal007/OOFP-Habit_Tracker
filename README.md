# OOFP-Habit_Tracker
Python based Habit tracker App built using OOP and FP


# Habit Tracker – Python CLI Application

A modular command line Habit Tracker built with Python and SQLite.

This application allows users to create daily or weekly habits, mark them as completed, track streaks, and analyze performance. Data is stored locally in a SQLite database.


# Requirments 

Python 3.10+


# Installation
## METHOD 1: Download ZIP 
### Step 1 Download from GitHub
- Go to GitHub repository page
- Click the green “Code” button
- Click “Download ZIP”
- Extract the ZIP file

You will now have a folder like:
- HABIT_TRACKER

### Step 2 Open Terminal in That Folder
Windows:
- Open the extracted HABIT_TRACKER folder
- Hold Shift + Right Click
- Click “Open PowerShell window here”
 or
 - “Open in Terminal”

OR manually:
- cd path\to\HABIT_TRACKER

### Step 3 (Optional) Create Virtual Environment
```python -m venv venv```

```venv\Scripts\activate```

### Step 4 Run the App
#### From inside the HABIT_TRACKER folder:
```python -m app.main```

If needed:
```python3 -m app.main```

- The app will start and show the menu.

### Step 5 Running Tests
From the HABIT_TRACKER folder:
``` python -m unittest discover -s tests -p "*.py" ```



## METHOD 2: Clone Using Git
### Step 1 Clone the Repository

git clone 

```cd HABIT_TRACKER```

### Step 2 Install (Optional Virtual Environment)

``` python -m venv venv ```

``` venv\Scripts\activate ```

### Step 3 Run the App
``` python -m app.main ```


### Step 4 Running Tests
From the HABIT_TRACKER folder:
``` python -m unittest discover -s tests -p "*.py" ```


# IMPORTANT:
- Run this command from the folder.Because the app is built from multiple modules, you need to launch it from the project’s main folder so it can find all the files it depends on. First, open a terminal and change into the project directory use your downloaded folder name. Then run the main program file to start the app.


# Running Unit Tests

## To run all tests:
``` python -m unittest discover -s tests -p "*.py" ```

## Tests:

- Filtering daily vs weekly habits

- Longest daily streak

- Longest weekly streak

- Insert habit and checkoff

- Cascade delete behavior

- Duplicate daily checkoff prevention


## The application will:

- Automatically create the SQLite database (habits.db)

- Create required tables

- Insert example habits and demo checkoffs

- Display the main menu


## Project Structure
```
HABIT_TRACKER/
├── app/                    # App code
│   ├── core/               # Habit + analytics logic
│   ├── db/                 # SQLite storage
│   ├── examples/           # Demo data
│   └── main.py             # Run the CLI
├── tests/                  # Unit tests
├── habits.db               # Auto created database
└── requirements.txt        # Dependencies
```

# Example Usage

## When the app starts, you will see:
--- Habit Tracker Menu ---
1) Show all habits
2) Create habit
3) Delete habit
4) Mark completed
5) Show history
6) Show daily/weekly habits
7) Show best streak
8) Show streak for one habit
0) Exit

## Here's the quick quide
## You need to enter what it asks for and and then press enter

Show all habits: Displays all stored habits with their type, last completion, and task.

Create habit: Adds a new daily or weekly habit to the database.

Delete habit: Removes a selected habit and all its associated checkoffs.

Mark completed: Records a completion for a habit (once per day/week only).

Show history: Shows all past completion timestamps.

Show daily/weekly habits: Filters and displays habits by periodicity.

Show best streak: Displays the habit with the longest streak overall.

Show streak for one habit: Shows the longest streak for a selected habit.

Exit: Closes the application safely.



