def join_words(words):

    if len(words) <= 1:
        return "".join(words)
    return ", ".join(words[:-1]) + " and " + words[-1]

def explain_eligibility(course):
    reasons = course["reasons"]
    matches = []
    if "Match subject preference" in reasons:
        matches.append("your fav subject")
    if "Match career goal" in reasons:
        matches.append("your career goal")

    if matches:
        prefs = "it matches " + join_words(matches)
    else:
        prefs = "it does not match your fav subject or career goal"

    extra = [r for r in reasons if r not in ["Meet all requirements", "Match subject preference", "Match career goal"]]
    parts = ["you meet all requirements", prefs] + extra
    return f"Eligible for {course['name']} because " + "; ".join(parts) + "."

def explain_ineligibility( course):
    parts = []
    for reason in course["reasons"]:
        if reason.startswith("Insufficient credits"):
            have, need = [int(w) for w in reason.replace(",", "").split() if w.isdigit()]
            parts.append(f"you need {need - have} more credits (you have {have}, it needs {need})")
        elif reason.startswith("Missing subjects "):
            subjects = sorted(reason[len("Missing subjects "):].split(", "))
            parts.append("you still need to pass " + join_words(subjects))
        else:
            parts.append(reason)
    return f"Not eligible for {course['name']} because " + join_words(parts) + "."

def explain_course(course):
    if course["is_eligible"]:
        return explain_eligibility(course) 
    return explain_ineligibility(course)


if __name__ == "__main__":
    for course in [
        {"name": "Computer Science", "is_eligible": True, "score": 3,
         "reasons": ["Meet all requirements", "Match subject preference", "Match career goal"]},
        {"name": "Data Science", "is_eligible": True, "score": 2,
         "reasons": ["Meet all requirements", "Match subject preference"]},
        {"name": "Geography", "is_eligible": True, "score": 0,
         "reasons": ["Meet all requirements"]},
        {"name": "Medicine", "is_eligible": False, "score": 0,
         "reasons": ["Insufficient credits: 30 completed, 55 required", "Missing subjects science, math"]},
        {"name": "Test", "is_eligible": False, "score": 0,
         "reasons": ["Something new"]}]:
        print(explain_course(course))