from knowledge_base import load_courses, load_rules, get_course_rules
from reasoning_engine import build_initial_facts, calculate_score

def backward_chaining(goal, known_facts, rules, triggered_rules):
    """start from goal and find out what rule leads to the goal
    """
    # already known
    if goal in known_facts:
        return True

    proven = False

    # find rules that conclude gaol
    for rule in rules:
        if rule["conclusion"] != goal:
            continue

        # condition become sub-goal
        if all(backward_chaining(c, known_facts,rules, triggered_rules) for c in rule["conditions"]):
            proven = True

        # record rule
        if rule["id"] not in [r["rule_id"] for r in triggered_rules]:
            triggered_rules.append({
                "rule_id": rule["id"],
                "conditions": rule["conditions"],
                "conclusion": rule["conclusion"]
            })

    return proven

def get_requirements(student, course):
    credits_good = student["credits"] >= course["hard"]["min_credits"]
    lines =[f"Min credits: {course['hard']['min_credits']} (you have {student['credits']}) " f"[{'met' if credits_good else 'NOT met'}]" ]

    passed = student.get("passed_subjects", [])
    for subject in course["hard"]["requires"]:
        lines.append(f"Passed subject: {subject} [{'met' if subject in passed else 'NOT met'}]")

    return lines

def get_soft_preferences(student, course):
    lines = []

    for key,label in [("fav_subject", "Favourite subject"), ("career_goal", "Career goal")]:
        wanted = course["soft"].get(key)

        if wanted is not None:
            lines.append(f"{label}: {wanted} [{'match' if student.get(key) == wanted else 'no match'}]")

    return lines

def find_course(courses, text):
    for course in courses:
        if course["name"].lower() == text.strip().lower():
            return course

    return None

if __name__ == "__main__":
    courses = load_courses()
    all_rules = load_rules()

    student ={
        "name": "John",
        "credits": 45,
        "passed_subjects": ["math", "science"],
        "fav_subject": "computing",
        "career_goal": "software"
    }

    # user pciks course
    print("Available courses:",",".join(c["name"] for c in courses))

    course = None
    while course is None:
        course = find_course(courses, input("\n Enter a course: "))

        if course is None:
            print("Course not found, try again.")

    # prove goal eligibility and rule conclusion for scoring
    facts = build_initial_facts(student, course)
    rules = get_course_rules(all_rules, course["_id"])
    eligible_goal = f"eligible:{course['_id']}"
    triggered_rules = []

    is_eligible = backward_chaining(eligible_goal, facts, rules, triggered_rules)

    for rule in rules:
        backward_chaining(rule["conclusion"], facts, rules, triggered_rules)

    score = calculate_score(triggered_rules, all_rules) if is_eligible else 0

    # output
    print(f"\n============{course['name']}============")
    print(f"Eligible: {'Yes' if is_eligible else 'No'}" + (f" (score: {score})" if is_eligible else ""))

    print("\nRequirements:")
    for line in get_requirements(student, course):
        print(f" - {line}")

    print("\nSoft Preferences:")
    for line in get_soft_preferences(student, course):
        print(f" - {line}")