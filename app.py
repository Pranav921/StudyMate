from nlp_parser import parse_user_input
from task_time_estimator import estimate_time
from scheduler import create_study_schedule
import re
import csv
from datetime import datetime

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

def ask_choice(prompt, choices, default=None):
    label = "/".join(choices)
    hint = f" (Enter for {default})" if default else ""
    while True:
        s = input(f"{prompt} [{label}]{hint}\n> ").strip().lower()
        if s == "" and default:
            return default
        if s in choices:
            return s
        print(f"  Please type one of: {', '.join(choices)}.")

def infer_total_days(deadline: str | None) -> int | None:
    if not deadline:
        return None
    s = deadline.lower().strip()
    m = re.search(r"in\s+(?P<num>\d+|one|two|three|four|five|six|seven|eight|nine|ten|a|an)\s+(?P<unit>days?|weeks?|months?)", s)
    if m:
        num = m.group("num")
        unit = m.group("unit")
        words = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"a":1,"an":1}
        n = int(num) if num.isdigit() else words.get(num, 0)
        if unit.startswith("day"): return n
        if unit.startswith("week"): return n * 7
        if unit.startswith("month"): return n * 30
    m = re.search(r"by\s+next\s+(week|month)", s)
    if m:
        return 7 if m.group(1) == "week" else 30
    return None

def export_schedule_csv(schedule, path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Day", "Description", "EstimatedHours"])
        for day_index, day in enumerate(schedule, start=1):
            if not day:
                continue
            for t in day:
                w.writerow([day_index, t["description"], t["estimated_time"]])

def split_oversized_tasks(tasks, hours_per_day):
    def detect_units(desc):
        s = desc.strip()
        patterns = [
            (r'^(?P<prefix>.*?)(?P<count>\d+)\s+(?P<unit>videos?)\b', 'videos'),
            (r'^(?P<prefix>.*?)(?P<count>\d+)\s+(?P<unit>chapters?)\b', 'chapters'),
            (r'^(?P<prefix>.*?)(?P<count>\d+)\s+(?P<unit>(?:practice\s+)?problems?)\b', 'problems'),
            (r'^(?P<prefix>.*?)(?P<count>\d+)\s+(?P<unit>flashcards?)\b', 'flashcards'),
        ]
        for pat, _ in patterns:
            m = re.search(pat, s, flags=re.IGNORECASE)
            if m:
                prefix = m.group('prefix').strip()
                count = int(m.group('count'))
                unit = m.group('unit')
                return prefix, count, unit
        return None, None, None

    def singularize(unit):
        return unit[:-1] if unit.lower().endswith('s') else unit

    out = []
    for t in tasks:
        desc = t["description"]
        dur = max(0.0, float(t["estimated_time"]))
        if hours_per_day and dur > hours_per_day:
            prefix, count, unit = detect_units(desc)
            if prefix is not None and count and dur > 0:
                per_unit = dur / count
                if per_unit >= hours_per_day:
                    parts = int(dur // hours_per_day)
                    rem = round(dur - parts * hours_per_day, 2)
                    for _ in range(parts):
                        out.append({"description": desc, "estimated_time": round(hours_per_day, 2)})
                    if rem > 1e-9:
                        out.append({"description": desc, "estimated_time": rem})
                    continue
                units_per_day = max(1, int(hours_per_day // per_unit))
                remaining = count
                while remaining > 0:
                    take = min(units_per_day, remaining)
                    chunk_hours = round(take * per_unit, 2)
                    u = unit if take != 1 else singularize(unit)
                    p = (prefix.rstrip() + " ") if prefix else ""
                    out.append({"description": f"{p}{take} {u}", "estimated_time": chunk_hours})
                    remaining -= take
                continue
            parts = int(dur // hours_per_day)
            rem = round(dur - parts * hours_per_day, 2)
            for _ in range(parts):
                out.append({"description": desc, "estimated_time": round(hours_per_day, 2)})
            if rem > 1e-9:
                out.append({"description": desc, "estimated_time": rem})
        else:
            out.append({"description": desc, "estimated_time": round(dur, 2)})
    return out

def main():
    print("📚 Welcome to StudyMate!\n")
    user_input = input("Describe your goal, deadline, and preferences:\n> ")
    parsed = parse_user_input(user_input)

    print("\n✅ Parsed Info:")
    print(f" - Goal: {parsed['goal']}")
    print(f" - Deadline: {parsed['deadline']}")
    print(f" - Preferences: {', '.join(parsed['learning_preferences']) or 'None'}")

    hours_per_day = ask_float("\nHow many hours can you study per day? (e.g. 3.5):\n> ")
    auto_days = infer_total_days(parsed.get("deadline"))
    if auto_days:
        total_days = ask_int(f"How many days do you want to spread your studying over? (Enter for {auto_days})\n> ", default=auto_days)
    else:
        total_days = ask_int("How many days do you want to spread your studying over?\n> ")

    mode = ask_choice("\nScheduling mode?", choices=["balanced","compact"], default="balanced")

    DEFAULTS = {
        "video_minutes_each": 30,
        "practice_minutes_per10": 60,
        "chapter_minutes_each": 45,
        "flash_minutes_per30": 15
    }

    print("\nEnter your study tasks (type 'done' to finish):")
    tasks = []
    while True:
        task_input = input("> ").strip()
        if task_input.lower() == "done":
            break

        estimated = estimate_time(task_input)
        lower = task_input.lower()

        if "video" in lower:
            m = re.search(r'(\d+)\s+videos?', lower)
            count = int(m.group(1)) if m else ask_int("  How many videos?\n  > ", default=1)
            minutes = ask_float(f"  How long is each video (in minutes)? (Enter for {DEFAULTS['video_minutes_each']})\n  > ",
                                default=DEFAULTS["video_minutes_each"])
            estimated = round((minutes * count) / 60, 2)

        elif "practice" in lower:
            m = re.search(r'(\d+)\s+practice', lower) or re.search(r'(\d+)\s+problems?', lower)
            total_problems = int(m.group(1)) if m else ask_int("  How many practice problems?\n  > ", default=10)
            per10 = ask_float(f"  Minutes to solve 10 problems? (Enter for {DEFAULTS['practice_minutes_per10']})\n  > ",
                              default=DEFAULTS["practice_minutes_per10"])
            estimated = round((per10 * (total_problems / 10)) / 60, 2)

        elif "chapter" in lower or "read" in lower:
            m = re.search(r'(\d+)\s+chapters?', lower)
            count = int(m.group(1)) if m else ask_int("  How many chapters?\n  > ", default=1)
            minutes = ask_float(f"  Minutes per chapter? (Enter for {DEFAULTS['chapter_minutes_each']})\n  > ",
                                default=DEFAULTS["chapter_minutes_each"])
            estimated = round((minutes * count) / 60, 2)

        elif "flashcard" in lower or "flash cards" in lower or "flash-cards" in lower:
            m = re.search(r'(\d+)\s+flashcards?', lower)
            total_cards = int(m.group(1)) if m else ask_int("  How many flashcards?\n  > ", default=30)
            per30 = ask_float(f"  Minutes to review 30 flashcards? (Enter for {DEFAULTS['flash_minutes_per30']})\n  > ",
                              default=DEFAULTS["flash_minutes_per30"])
            estimated = round((per30 * (total_cards / 30)) / 60, 2)

        tasks.append({"description": task_input, "estimated_time": round(max(0.0, estimated), 2)})

    if not tasks:
        print("❌ No tasks entered. Exiting.")
        return

    tasks = split_oversized_tasks(tasks, hours_per_day)
    schedule = create_study_schedule(tasks, total_days, hours_per_day, mode=mode)

    print("\n📅 Your Study Plan:")
    for i, day in enumerate(schedule):
        if not day:
            continue
        print(f"\nDay {i + 1}:")
        for task in day:
            print(f" - {task['description']} ({task['estimated_time']} hrs)")
        total_time = round(sum(t['estimated_time'] for t in day), 2)
        print(f"  Total: {total_time} hours")

    save = input("\nSave this plan to CSV? (Y/N) ").strip().lower()
    if save == "y":
        fname = f"studymate_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        export_schedule_csv(schedule, fname)
        print(f"✅ Saved: {fname}")

if __name__ == "__main__":
    main()
