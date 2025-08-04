def create_study_schedule(tasks, total_days, hours_per_day):
    # Initialize schedule: one list per day
    schedule = [[] for _ in range(total_days)]
    day_totals = [0.0] * total_days  # Tracks total hours scheduled per day

    for task in tasks:
        scheduled = False
        for day in range(total_days):
            if day_totals[day] + task["estimated_time"] <= hours_per_day:
                schedule[day].append(task)
                day_totals[day] += task["estimated_time"]
                scheduled = True
                break
        # If task doesn't fit in any day, force it into the last day
        if not scheduled:
            schedule[-1].append(task)
            day_totals[-1] += task["estimated_time"]

    return schedule

if __name__ == "__main__":
    tasks = [
        {"description": "Watch 3 videos and solve 20 practice problems", "estimated_time": 3.5},
        {"description": "Read 2 chapters and review 60 flashcards", "estimated_time": 4.0},
        {"description": "Take a quiz and write a summary", "estimated_time": 1.75},
        {"description": "Solve 10 practice and read 1 chapter", "estimated_time": 2.5}
    ]

    total_days = 3
    hours_per_day = 4

    schedule = create_study_schedule(tasks, total_days, hours_per_day)

    for i, day in enumerate(schedule):
        print(f"\nDay {i + 1} schedule:")
        for task in day:
            print(f" - {task['description']} ({task['estimated_time']} hrs)")
        print(f"  Total: {round(sum(t['estimated_time'] for t in day), 2)} hours")
