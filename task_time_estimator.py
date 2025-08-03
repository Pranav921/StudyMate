import re

# Average time estimates per task (in hours)
TASK_TIME_TABLE = {
    "video": 0.5,          # per video
    "practice": 1.0,       # per 10 problems
    "reading": 1.5,        # per chapter
    "flashcards": 0.5,     # per 30 cards
    "quiz": 0.75,          # per quiz
    "summary": 1.0         # per topic
}

def estimate_time(task_description):
    task_description = task_description.lower()
    estimated_hours = 0.0

    # Estimate time for videos
    video_match = re.search(r'(\d+)\s+videos?', task_description)
    if video_match:
        count = int(video_match.group(1))
        estimated_hours += count * TASK_TIME_TABLE["video"]

    # Practice problems
    practice_match = re.search(r'(\d+)\s+practice', task_description)
    if practice_match:
        count = int(practice_match.group(1))
        estimated_hours += (count / 10) * TASK_TIME_TABLE["practice"]

    # Reading chapters
    reading_match = re.search(r'(\d+)\s+chapters?', task_description)
    if reading_match:
        count = int(reading_match.group(1))
        estimated_hours += count * TASK_TIME_TABLE["reading"]

    # Flashcards
    flashcard_match = re.search(r'(\d+)\s+flashcards?', task_description)
    if flashcard_match:
        count = int(flashcard_match.group(1))
        estimated_hours += (count / 30) * TASK_TIME_TABLE["flashcards"]

    # Quizzes
    quiz_match = re.search(r'\bquiz\b|\bquizzes\b', task_description)
    if quiz_match:
        estimated_hours += TASK_TIME_TABLE["quiz"]

    # Summaries
    summary_match = re.search(r'\bsummary\b|\bsummaries\b', task_description)
    if summary_match:
        estimated_hours += TASK_TIME_TABLE["summary"]

    return round(estimated_hours, 2)

# Test the Estimator

if __name__ == "__main__":
    test_inputs = [
        "Watch 3 videos and solve 20 practice problems",
        "Read 2 chapters and review 60 flashcards",
        "Take a quiz and write a summary",
        "Solve 10 practice and read 1 chapter"
    ]

    for task in test_inputs:
        estimated = estimate_time(task)
        print(f"{task} → Estimated Time: {estimated} hours")
