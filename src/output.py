from explanation import explain_course

def format_report(student, ranked, ineligible):
    lines = [f"Recommendation for {student['name']} ({student['credits']} credits)", ""]

    if ranked:
        best = ranked[0]
        lines.append(f"Best match: {best['name']} (score {best['score']})")
        lines.append("  " + explain_course(best))
        if len(ranked) > 1:
            lines.append("")
            lines.append("Other eligible courses:")
            for course in ranked[1:]:
                lines.append(f"  {course['rank']}. {explain_course(course)}")
    else:
        lines.append("You are not eligible for any course yet. Here is what you still need:")

    if ineligible:
        lines.append("")
        lines.append("Not eligible:")
        for course in ineligible:
            lines.append("  - " + explain_course(course))

    return "\n".join(lines)


def format_check(result):
    if result["is_eligible"]:
        status = f"eligible (score {result['score']})"
    else:
        status = "not eligible"
    lines = [f"{result['course']}: {status}", "", "Requirements:"]
    lines += ["  - " + line for line in result["requirements"]]
    lines += ["", "Preferences:"]
    lines += ["  - " + line for line in result["preferences"]]
    return "\n".join(lines)


def print_report(student, ranked, ineligible):
    print(format_report(student, ranked, ineligible))


def print_check(result):
    print(format_check(result))


if __name__ == "__main__":
    from main import recommend
    from student_input import parse_typed_student

    for answers in [
        {"name": "John", "credits": "67", "passed_subjects": "math, science", "fav_subject": "computing", "career_goal": "software"},
        {"name": "Grace", "credits": "38", "passed_subjects": "", "fav_subject": "computing", "career_goal": "research"},
        {"name": "Sam", "credits": "20", "passed_subjects": "", "fav_subject": "art", "career_goal": "music"}]:
        ranked, ineligible = recommend(answers)
        print_report(parse_typed_student(answers), ranked, ineligible)
        print("-" * 60)

    print_check({"course": "Physics", "is_eligible": False, "score": 0,
                 "requirements": ["Min credits: 45 (you have 38) [NOT met]", "Passed subject: math [NOT met]"],
                 "preferences": ["Favourite subject: science [no match]", "Career goal: research [match]"]})
