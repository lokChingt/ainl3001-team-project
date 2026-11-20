from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
folder_path = ROOT / "data"

def load_rules():
    with open(f"{folder_path}/rules.json", "r") as file:
        return json.load(file)

def get_course_rules(rules, course_id):
    course_rules = []

    for rule in rules:
        course_rules.append({
            "id": rule["id"],
            "conditions": [
                condition.format(course_id = course_id)
                for condition in rule["conditions"]
            ],
            "conclusion": rule["conclusion"].format(
                course_id = course_id
            )
        })

    return course_rules