
import json
from pathlib import Path
from knowledge_base import FACT_NAMES

REQUIRED_KEYS = {"name", "credits", "passed_subjects", "fav_subject", "career_goal"}
DEFAULT_PATH = Path(__file__).parent.parent / "data" / "students.json"
ALIASES = {"maths": "math", "mathematics": "math"}

def normalise(subject: str) -> str:
    """lowercase, trim and map aliases to match math"""
    s = subject.strip().lower()
    return ALIASES.get(s, s)

def parse_credits(text: str) -> int:
    """Turn typed ' 30 ' into 30 (text into num) + Raise eror if not cele number."""
    try:
        return int(text.strip())
    except ValueError:
        raise ValueError(f"Credits must be a whole number like 67, you typed {text!r}")

def parse_subjects(text: str) -> list[str]:
    """Turn typed 'Math, science' into ['math', 'science'] + empty = no sub passed."""
    result = []
    for s in text.split(","):
        if s.strip():
            result.append(normalise(s))
    return result

def validate_student(raw: dict) -> dict:
    """
    
    - Check one student dict
    - return a clean copy
    - Raise ValueError if anything is wrong

    """

    if not isinstance(raw, dict):
        raise ValueError("Student must be an object")
    
    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise ValueError(f"Student {raw.get('name', '?')}: missing key {sorted(missing)}")
    
    name = raw["name"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Student has an empty or invalid name")
    name = name.strip()

    credits = raw["credits"]
    if isinstance(credits, bool) or not isinstance(credits, int) or credits < 0:
        raise ValueError(f"{name}: credits must be a whole number, 0 or more, got {credits!r}")

    subjects = raw["passed_subjects"]
    if not isinstance(subjects, list) or not all(isinstance(s, str) for s in subjects):
        raise ValueError(f"{name}: passed_subjects must be a list of strings, got {subjects!r}")  

    subjects = [s.strip().lower() for s in subjects]
    unknown = set(subjects) - FACT_NAMES
    if unknown:
        raise ValueError(f"{name}: passed_subjects has unknown subject(s) {sorted(unknown)}. Valid: {sorted(FACT_NAMES)}")

    prefs = {}
    for key in ["fav_subject", "career_goal"]:
        value = raw[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name}: {key} must be a non empty text, got {value!r}")
        prefs[key] = value.strip().lower()

    return {
        "name": name,
        "credits": credits,
        "passed_subjects": subjects,
        "fav_subject": prefs["fav_subject"],
        "career_goal": prefs["career_goal"]
    }

def parse_typed_student(answers: dict) -> dict:
    """turn typed student input into clean student"""
    student = {
        "name": answers.get("name", ""),
        "credits": parse_credits(answers.get("credits", "")),
        "passed_subjects": parse_subjects(answers.get("passed_subjects", "")),
        "fav_subject": normalise(answers.get("fav_subject", "")),
        "career_goal": answers.get("career_goal", ""),
    }
    return validate_student(student)



def load_students(path=DEFAULT_PATH) -> list[dict]:
    """

    -Read the JSON file
    -validate every student
    -reject duplicates
    -return the list

    """

    path = Path(path)
    try: 
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
            raise ValueError(f"{path} is not valid JSON: {e}")

    students = [validate_student(s) for s in data.get("students", [])]
    if not students:
        raise ValueError(f"{path} has no students")

    names = [s["name"] for s in students]
    if len(names) != len(set(names)):
        raise ValueError(f"{path} has duplicate student names")
    return students



'Test(s):'

if __name__ == "__main__":
    for bad in ["John", {"name": "X"},
                {"name": "  ", "credits": 1, "passed_subjects": ["math", "science"], "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": "80", "passed_subjects": ["math", "science"], "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": -5, "passed_subjects": ["math", "science"], "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": True, "passed_subjects": ["math", "science"], "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": 1.5, "passed_subjects": ["math", "science"], "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": 50, "passed_subjects": "math", "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": 50, "passed_subjects": [1, 2], "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": 50, "passed_subjects": ["maths"], "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": 50, "passed_subjects": [], "fav_subject": "   ", "career_goal": "b"},
                {"name": "X", "credits": 50, "passed_subjects": [], "fav_subject": "a", "career_goal": 5}]:
        try:
            validate_student(bad)
            print("NOT rejected:", bad)
        except ValueError as e:
            print("OK, rejected:", e)

    good = {"name": "X", "credits": 67, "passed_subjects": [" Math ", "science"],
            "fav_subject": " Computing ", "career_goal": " SOFTWARE "}
    print("OK, accepted:", validate_student(good))       

    print("parse_credits typed input ")
    for typed in ["80", " 67 ", "0"]:
        print("OK, parsed:", repr(typed), "->", parse_credits(typed))
    for typed in ["eighty", "6.7", "", "6 7"]:
        try:
            parse_credits(typed)
            print("NOT rejected:", repr(typed))
        except ValueError as e:
            print("OK, rejected:", e)

    print("parse_subjects typed input")
    for typed in ["math, science", " Math ,SCIENCE ", "", "math,,"]:
        print("OK, parsed:", repr(typed), "->", parse_subjects(typed))
        
    print("load_students")
    print("OK, loaded:", len(load_students()), "students")
    for bad in ["missing.json", "data/course.json"]:
        try:
            load_students(bad)
            print("NOT rejected:", bad)
        except (ValueError, FileNotFoundError) as e:
            print("OK, rejected:", e)

    print("parse_typed_student")
    print("OK, accepted:", parse_typed_student({"name": " Karla ", "credits": " 67 ",
          "passed_subjects": "Math, science", "fav_subject": " Computing", "career_goal": "SOFTWARE"}))
    for bad in [{"name": "Karla", "credits": "eighty", "passed_subjects": "math", "fav_subject": "a", "career_goal": "b"},
                {"name": "Karla", "credits": "67", "passed_subjects": "math, art", "fav_subject": "a", "career_goal": "b"},
                {"name": "Karla", "credits": "67", "passed_subjects": "", "fav_subject": "", "career_goal": "b"}]:
        try:
            parse_typed_student(bad)
            print("NOT rejected:", bad)
        except ValueError as e:
            print("OK, rejected:", e)