import spacy
import re
nlp = spacy.load("en_core_web_sm")

LEARNING_STYLES = ["videos", "practice", "reading", "flashcards", "quizzes", "projects"]

def _extract_goal_text(user_input: str):
    text = user_input.strip()
    pattern = re.compile(
        r"(?:study|learn|prepare|prep)(?:\s+for)?\s+(?P<goal>.+?)\s*(?:"
        r"in\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|a|an)\s+(?:days?|weeks?|months?)|"
        r"by\s+next\s+(?:week|month)|"
        r"using\b|with\b|for\b|before\b|on\b|by\b|\.|,|$)",
        flags=re.IGNORECASE
    )
    m = pattern.search(text)
    if m:
        goal = m.group("goal").strip(" .,:;!")
        goal = re.sub(r"^(?:for\s+)?(?:a|an|the)\s+", "", goal, flags=re.IGNORECASE)
        return goal if goal else None

    doc = nlp(text)
    noun_chunks = [
        chunk.text.strip()
        for chunk in doc.noun_chunks
        if chunk.root.pos_ != "PRON" and chunk.text.lower() not in {"i", "me", "my"}
    ]
    if noun_chunks:
        noun_chunks.sort(key=len, reverse=True)
        return noun_chunks[0]

    ents = [
        ent.text for ent in doc.ents
        if ent.text.lower() not in {"i", "me", "my"} and ent.label_ in {
            "ORG", "PRODUCT", "WORK_OF_ART", "EVENT", "LANGUAGE", "PERSON"
        }
    ]
    if ents:
        ents.sort(key=len, reverse=True)
        return ents[0]
    return None

def parse_user_input(user_input):
    goal = _extract_goal_text(user_input)
    deadline_match = re.search(
        r"(in\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|a|an)\s+(?:days?|weeks?|months?)|"
        r"by\s+next\s+(?:week|month))",
        user_input.lower()
    )
    deadline = deadline_match.group() if deadline_match else None
    learning_preferences = [s for s in LEARNING_STYLES if s in user_input.lower()]
    return {
        "goal": goal,
        "deadline": deadline,
        "learning_preferences": learning_preferences
    }

if __name__ == "__main__":
    test_input = "I want to study for a Math midterm in 10 days using videos, practice, reading, and flashcards."
    print(parse_user_input(test_input))
