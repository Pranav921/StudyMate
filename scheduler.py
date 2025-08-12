from typing import List, Dict

def create_study_schedule(
    tasks: List[Dict[str, float]],
    total_days: int,
    hours_per_day: float,
    mode: str = "balanced"
):
    schedule = [[] for _ in range(total_days)]
    day_totals = [0.0] * total_days
    work = tasks[:]
    if mode == "balanced":
        work.sort(key=lambda t: t["estimated_time"], reverse=True)

    for task in work:
        dur = max(0.0, float(task["estimated_time"]))
        placed = False

        if mode == "balanced":
            for day in sorted(range(total_days), key=lambda d: day_totals[d]):
                if day_totals[day] + dur <= hours_per_day:
                    schedule[day].append(task)
                    day_totals[day] += dur
                    placed = True
                    break
        else:
            for day in range(total_days):
                if day_totals[day] + dur <= hours_per_day:
                    schedule[day].append(task)
                    day_totals[day] += dur
                    placed = True
                    break

        if not placed:
            schedule[-1].append(task)
            day_totals[-1] += dur

    return schedule

if __name__ == "__main__":
    tasks = [
        {"description": "Watch 6 videos", "estimated_time": 2.5},
        {"description": "Solve 40 practice problems", "estimated_time": 1.33},
        {"description": "Read 3 chapters", "estimated_time": 2.5},
        {"description": "Review 120 flashcards", "estimated_time": 1.0},
    ]
    total_days = 4
    hours_per_day = 3
    schedule = create_study_schedule(tasks, total_days, hours_per_day, mode="balanced")
    for i, day in enumerate(schedule):
        print(f"\nDay {i+1}:")
        for t in day:
            print(f" - {t['description']} ({t['estimated_time']} hrs)")
        print(f"  Total: {round(sum(t['estimated_time'] for t in day), 2)} hours")
