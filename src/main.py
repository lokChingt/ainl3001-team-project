from student_input import parse_typed_student
from knowledge_base import load_courses, load_rules
from reasoning_engine import evaluate_courses


def recommend(answers:dict):
    """typed answers get cleaned then return ranked + ineligible courses"""
    student = parse_typed_student(answers)
    ranked, ineligible = evaluate_courses(student, load_courses(), load_rules())
    return ranked, ineligible





if __name__ == "__main__":
    ranked, ineligible = recommend({"name": "John", "credits": " 67 ", "passed_subjects": "Math, science",
                                    "fav_subject": "computing", "career_goal": "software"})
    print("OK, 1st:", ranked[0]["name"])
    clean, _ = recommend({"name": "John", "credits": "67", "passed_subjects": "math, science",
                          "fav_subject": "computing", "career_goal": "software"})
    print("OK, same as clean:", [c["name"] for c in ranked] == [c["name"] for c in clean])

    try:
        recommend({"name": "John", "credits": "eighty", "passed_subjects": "math",
                   "fav_subject": "computing", "career_goal": "software"})
        print("NOT rejected: eighty")
    except ValueError as e:
        print("OK, rejected:", e)