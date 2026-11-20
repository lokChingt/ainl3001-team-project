import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent/ "data"/ "course.json"

FACT_NAMES = {"math", "science"}

def load_courses(path=DEFAULT_PATH):
    """Read file and validate the data types and return a list of coursrs dictionaries"""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))

    except FileNotFoundError:
        raise FileNotFoundError(f"Rules file not found: {path}")
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Rules file not valid JSON: {e}")
    courses = []
    seen_names = set()
    seen_ids = set()

    for c in raw.get("courses", []):
        name = c.get("name")

        if not name:
            raise ValueError("A couse is missing the 'name'")

        if name in seen_names:
            raise ValueError(f"Duplicate course: {name}")
        
        seen_names.add(name)

        course_id = c.get("_id")
        if not isinstance(course_id, str) or not course_id.strip():
            raise ValueError(f"{name}: '_id' is missing")
        course_id = course_id.strip()
        if course_id in seen_ids:
            raise ValueError(f"{name} is duplicate _id")
        seen_ids.add(course_id)

        hard = c.get("hard", {})
        soft = c.get("soft", {})

        if not isinstance(hard.get("min_credits"), int) or hard["min_credits"] < 0:
            raise ValueError(f"{name}: 'min_credits' must be an non-negative number")

        unknown = set(hard.get("requires", [])) - FACT_NAMES

        if unknown:
            raise ValueError(f"{name}: unkown required facts {sorted(unknown)}")

        for key in ("fav_subject", "career_goal"):
            if not isinstance(soft.get(key), str) or not soft[key].strip():
                raise ValueError(f"{name}: soft preference '{key}' is empty")


        courses.append({
            "_id": course_id,
            "name": name,
            "hard": {"min_credits": hard["min_credits"], "requires": list(hard.get("requires", []))},
            "soft": {"fav_subject": soft["fav_subject"].strip().lower(), "career_goal": soft["career_goal"].strip().lower()}
        })

    if not courses:
        raise  ValueError("Course not in file")
    return courses


if __name__ == "__main__":
    courses = load_courses()
    print(f"Loaded {len(courses)} courses")
    for c in courses:
        print(c["_id"],c["name"], c["hard"], c["soft"])