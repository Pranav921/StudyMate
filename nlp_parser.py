import spacy
import re

nlp = spacy.load("en_core_web_sm")

LEARNING_STYLES = ["videos", "practice", "reading", "flashcards", "quizzes", "projects"]

def parse_user_input(user_input):
    doc = nlp(user_input)

    goal = None
    deadline = None
    learning_preferences = []

    # Extract Goal (Subject)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART", "EVENT", "LANGUAGE", "PERSON"]:
            goal = ent.text

    # Fallback for goal (catch noun chunks if no entity detected)
    if not goal:
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        if noun_chunks:
            goal = noun_chunks[0]

    # Extract Deadline (FIXED REGEX for plural and singular forms)
    deadline_match = re.search(
    r"(in\s+\d+\s+(?:days|day|weeks|week|months|month)|by\s+next\s+(?:week|month))",
    user_input.lower()
    )
    if deadline_match:
        deadline = deadline_match.group()

    # Extract Learning Preferences
    for style in LEARNING_STYLES:
        if style in user_input.lower():
            learning_preferences.append(style)

    return {
        "goal": goal,
        "deadline": deadline,
        "learning_preferences": learning_preferences
    }

# Test
if __name__ == "__main__":
    test_input = "I want to learn Data Structures by next month using videos and projects."
    result = parse_user_input(test_input)
    print(result)
