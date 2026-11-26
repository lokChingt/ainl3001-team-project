import sys
from student_input import parse_typed_student
from knowledge_base import load_courses, load_rules, get_course_rules
from reasoning_engine import evaluate_courses, build_initial_facts, calculate_score
from backward_chaining import backward_chaining, get_requirements, get_soft_preferences, find_course
from output import print_report, print_check

# loop through list only write questions once
FIELDS= [("name", "Name"), ("credits", "Credits Completed"), ("passed_subjects", "Passed subjects (comma separated)"), ("fav_subject", "Favourite subject"), ("career_goal", "Career goal")]

def header(title):
    """print a title inside a banner, used to separate sections of output"""
    print(f"\n{'='*40}\n{title.center(40)}\n{'=' * 40}")

def recommend(answers:dict):
    """typed answers get cleaned then return ranked + ineligible courses"""
    # validate and clean raw text
    student = parse_typed_student(answers)
    ranked, ineligible = evaluate_courses(student, load_courses(), load_rules())
    return ranked, ineligible

def check_course(student, course, all_rules):
    
    # facts from students data
    facts = build_initial_facts(student, course)

    # only specific course rules
    rules =  get_course_rules(all_rules, course["_id"])
    triggered = []

    # prove the goal is student eligivle for course
    eligible = backward_chaining(f"eligible:{course['_id']}", facts, rules, triggered)

    # prove other conclusion so soft prefernces are recorded and counted torwards score
    for rule in rules:
        backward_chaining(rule["conclusion"], facts, rules, triggered)

        # only eligible courses get score
    return eligible, calculate_score(triggered, all_rules) if eligible else 0

def get_student():
    """ask the 5 questions, keep asking until the answers are valid"""
    while True:
        answers = {key: input(f" {label}: ") for key, label in FIELDS}

        try:
            # raise valueerror on bad input
            return parse_typed_student(answers)
        except ValueError as e:
            print(f" ! {e}\n Please try again.")

def show_recommendations(student, courses, rules):
    """option 1: forward chaining, ranked list + ineligible list"""
    ranked, ineligible = evaluate_courses(student, courses, rules)

    header("Recommended Courses")
    print_report(student, ranked, ineligible)

def course_check(student, courses, rules):
    """option 2: backward chaining on one course the user picks"""
    print("\nCourses: "+",".join(c["name"] for c in courses))

    # find_course matches name and returns none if course does not exist
    course = find_course(courses, input("Enter a course: "))

    if course is None:
        print("! Course not found")
        return

    eligible, score = check_course(student, course, rules)
    header(course["name"])

    print_check({"course": course["name"], "is_eligible": eligible, "score": score,
                 "requirements": get_requirements(student, course),
                 "preferences": get_soft_preferences(student, course)})


def main():
    """load the knowledge base, get the student, then loop on the menu"""
    courses, rules = load_courses(), load_rules()
    header("Course Recommendation System")
    student = get_student()

    while True:
        choice = input("\n [1] Recommend Course\n [2] Check Course\n [3] Change student\n [4] Quit\n\n Choose:").strip()

        if choice == "1":
            show_recommendations(student,courses,rules)

        elif choice == "2":
            course_check(student, courses, rules)

        elif choice == "3":
            student = get_student()

        elif choice == "4":
            break
        else:
            print("! Enter 1-4")

def run_tests():
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

if __name__ == "__main__":
    try:
        
        run_tests() if "--test" in sys.argv else main()
    except (KeyboardInterrupt, EOFError): 
        print("\nGoodbye!")