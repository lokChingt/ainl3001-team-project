import json
from pathlib import Path

FACT_NAMES = {"passed_math", "passed_science"}

def load_courses(path="data/course.json"):
    """Read file and validate the data types and return a list of coursrs dictionaries"""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))

    except FileNotFoundError:
        raise FileNotFoundError(f"Rules file not found: {path}")
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Rules file not valid JSON: {e}")
    courses = []
    seen = set()

    for c in raw.get("courses", []):
        name = c.get("name")

        if not name:
            raise ValueError("A couse is missing the 'name'")

        if name in seen:
            raise ValueError(f"Duplicate course: {name}")
        
        seen.add(name)

        hard = c.get("hard", {})
        soft = c.get("soft", {})

        if not isinstance(hard.get("min_credits"), int) or hard["min_credits"] < 0:
            raise ValueError(f"{name}: 'credits_above' must be an non-negative number")

        unknown = set(hard.get("requires", [])) - FACT_NAMES

        if unknown:
            raise ValueError(f"{name}: unkown required facts {sorted(unknown)}")

        for key in ("fav_subject", "career_goal"):
            if not isinstance(soft.get(key), str) or not soft[key].strip():
                raise ValueError(f"{name}: soft preference '{key}' is empty")


        courses.append({
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
        print(c["name"], c["hard"], c["soft"])