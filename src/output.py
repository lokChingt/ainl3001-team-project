from explanation import explain_course

def format_report(student, ranked, ineligible):
    lines = [f"Recommendation for {student['name']} ({student['credits']} credits)", ""]
