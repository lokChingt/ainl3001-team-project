
import json
from pathlib import Path

REQUIRED_KEYS = {"name", "credits", "passed_math", "passed_science", "fav_subject", "career_goal"}
DEFAULT_PATH = Path(__file__).parent.parent / "data" / "students.json"

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
        raise ValueError("Student has an empty or invalid Nname")
    name = name.strip()





def load_students(path=...) -> list[dict]:
    """

    -Read the JSON file
    -validate every student
    -reject duplicates
    -return the list

    """

    

'Test(s):'

'''
if __name__ == "__main__":
    for bad in ["John", {"name": "X"}, {"name": "  ", "credits": 1, "passed_math": True,
                "passed_science": True, "fav_subject": "a", "career_goal": "b"}]:
        try:
            validate_student(bad)
            print("NOT rejected:", bad)
        except ValueError as e:
            print("OK, rejected:", e)
        
'''
