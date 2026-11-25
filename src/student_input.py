
import json
from pathlib import Path

REQUIRED_KEYS = {"name", "credits", "passed_math", "passed_science", "fav_subject", "career_goal"}
DEFAULT_PATH = Path(__file__).parent.parent / "data" / "students.json"

def parse_credits(text: str) -> int:
    """Turn typed ' 30 ' into 30 (text into num) + Raise eror if not cele number."""
    try:
        return int(text.strip())
    except ValueError:
        raise ValueError(f"Credits must be a whole number like 67, you typed {text!r}")

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





def load_students(path=...) -> list[dict]:
    """

    -Read the JSON file
    -validate every student
    -reject duplicates
    -return the list

    """



'Test(s):'

if __name__ == "__main__":
    for bad in ["John", {"name": "X"},
                {"name": "  ", "credits": 1, "passed_math": True,
                 "passed_science": True, "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": "80", "passed_math": True,
                 "passed_science": True, "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": -5, "passed_math": True,
                 "passed_science": True, "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": True, "passed_math": True,
                 "passed_science": True, "fav_subject": "a", "career_goal": "b"},
                {"name": "X", "credits": 1.5, "passed_math": True,
                 "passed_science": True, "fav_subject": "a", "career_goal": "b"}]:
        try:
            validate_student(bad)
            print("NOT rejected:", bad)
        except ValueError as e:
            print("OK, rejected:", e)

    print("parse_credits typed input ")
    for typed in ["80", " 67 ", "0"]:
        print("OK, parsed:", repr(typed), "->", parse_credits(typed))
    for typed in ["eighty", "6.7", "", "6 7"]:
        try:
            parse_credits(typed)
            print("NOT rejected:", repr(typed))
        except ValueError as e:
            print("OK, rejected:", e)
