
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





def load_students(path=...) -> list[dict]:
    """

    -Read the JSON file
    -validate every student
    -reject duplicates
    -return the list

    """