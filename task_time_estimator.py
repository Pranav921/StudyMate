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

    video_match = re.search(r'(\d+)\s+videos?', task_description)
    if video_match:
        count = int(video_match.group(1))
        estimated_hours += count * TASK_TIME_TABLE["video"]

    practice_match = re.search(r'(\d+)\s+practice', task_description)
    if practice_match:
        count = int(practice_match.group(1))
        estimated_hours += (count / 10) * TASK_TIME_TABLE["practice"]

    reading_match = re.search(r'(\d+)\s+chapters?', task_description)
    if reading_match:
        count = int(reading_match.group(1))
        estimated_hours += count * TASK_TIME_TABLE["reading"]

    flashcard_match = re.search(r'(\d+)\s+flashcards?', task_description)
    if flashcard_match:
        count = int(flashcard_match.group(1))
        estimated_hours += (count / 30) * TASK_TIME_TABLE["flashcards"]

    quiz_match = re.search(r'\bquiz\b|\bquizzes\b', task_description)
    if quiz_match:
        estimated_hours += TASK_TIME_TABLE["quiz"]

    summary_match = re.search(r'\bsummary\b|\bsummaries\b', task_description)
    if summary_match:
        estimated_hours += TASK_TIME_TABLE["summary"]

    return round(estimated_hours, 2)
