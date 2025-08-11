from nlp_parser import parse_user_input
from task_time_estimator import estimate_time
from scheduler import create_study_schedule
import re

# --- small input helpers ---
def ask_int(prompt, default=None):
    while True:
        s = input(prompt).strip()
        if s == "" and default is not None:
            return default
        try:
            return int(s)
        except ValueError:
            print("  Please enter a whole number." if default is None else f"  Please enter a whole number (or press Enter for {default}).")

def ask_float(prompt, default=None):
    while True:
        s = input(prompt).strip()
        if s == "":
            return default
        try:
            return float(s)
        except ValueError:
            print("  Please enter a number." if default is None else f"  Please enter a number (or press Enter for {default}).")

def main():
    print("📚 Welcome to StudyMate!\n")

    user_input = input("Describe your goal, deadline, and preferences:\n> ")
    parsed = parse_user_input(user_input)

    print("\n✅ Parsed Info:")
    print(f" - Goal: {parsed['goal']}")
    print(f" - Deadline: {parsed['deadline']}")
    print(f" - Preferences: {', '.join(parsed['learning_preferences']) or 'None'}")

    # availability
    hours_per_day = ask_float("\nHow many hours can you study per day? (e.g. 3.5):\n> ")
    total_days = ask_int("How many days do you want to spread your studying over?\n> ")

    # defaults (used if the user presses Enter at override prompts)
    DEFAULTS = {
        "video_minutes_each": 30,       # per video
        "practice_minutes_per10": 60,   # per 10 problems
        "chapter_minutes_each": 45,     # per chapter
        "flash_minutes_per30": 15       # per 30 cards
    }

    print("\nEnter your study tasks (type 'done' to finish):")
    tasks = []
    while True:
        task_input = input("> ").strip()
        if task_input.lower() == "done":
            break

        # start with fallback estimate (works when numbers are present)
        estimated = estimate_time(task_input)
        lower = task_input.lower()

        # VIDEOS
        if "video" in lower:
            # count
            m = re.search(r'(\d+)\s+videos?', lower)
            count = int(m.group(1)) if m else ask_int("  How many videos?\n  > ", default=1)
            # duration
            minutes = ask_float(f"  How long is each video (in minutes)? (Enter for {DEFAULTS['video_minutes_each']})\n  > ",
                                default=DEFAULTS["video_minutes_each"])
            estimated = round((minutes * count) / 60, 2)

        # PRACTICE PROBLEMS
        elif "practice" in lower:
            m = re.search(r'(\d+)\s+practice', lower) or re.search(r'(\d+)\s+problems?', lower)
            # If no explicit count, ask for total problems
            total_problems = int(m.group(1)) if m else ask_int("  How many practice problems?\n  > ", default=10)
            per10 = ask_float(f"  Minutes to solve 10 problems? (Enter for {DEFAULTS['practice_minutes_per10']})\n  > ",
                              default=DEFAULTS["practice_minutes_per10"])
            estimated = round((per10 * (total_problems / 10)) / 60, 2)

        # READING (CHAPTERS)
        elif "chapter" in lower or "read" in lower:
            m = re.search(r'(\d+)\s+chapters?', lower)
            count = int(m.group(1)) if m else ask_int("  How many chapters?\n  > ", default=1)
            minutes = ask_float(f"  Minutes per chapter? (Enter for {DEFAULTS['chapter_minutes_each']})\n  > ",
                                default=DEFAULTS["chapter_minutes_each"])
            estimated = round((minutes * count) / 60, 2)

        # FLASHCARDS
        elif "flashcard" in lower or "flash cards" in lower or "flash-cards" in lower:
            m = re.search(r'(\d+)\s+flashcards?', lower)
            total_cards = int(m.group(1)) if m else ask_int("  How many flashcards?\n  > ", default=30)
            per30 = ask_float(f"  Minutes to review 30 flashcards? (Enter for {DEFAULTS['flash_minutes_per30']})\n  > ",
                              default=DEFAULTS["flash_minutes_per30"])
            estimated = round((per30 * (total_cards / 30)) / 60, 2)

        # QUIZ / SUMMARY keep fallback from estimator (0.75 / 1.0) — nothing to ask

        tasks.append({"description": task_input, "estimated_time": estimated})

    if not tasks:
        print("❌ No tasks entered. Exiting.")
        return

    schedule = create_study_schedule(tasks, total_days, hours_per_day)

    print("\n📅 Your Study Plan:")
    for i, day in enumerate(schedule):
        print(f"\nDay {i + 1}:")
        for task in day:
            print(f" - {task['description']} ({task['estimated_time']} hrs)")
        total_time = round(sum(t['estimated_time'] for t in day), 2)
        print(f"  Total: {total_time} hours")

if __name__ == "__main__":
    main()
