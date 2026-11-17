from loader import load_courses

def check_eligible(student, course):
    # return each course
        # eligible: bool, 
        # reasons: list[]

    reasons = []

    # check credits
    if student["credits"] < course["credits_above"]:
        reasons.append(f"Insufficient credits: {course["credits_above"]} credits required")

    # check required subjects
    missing_subjects = set(course["requires"]) - set(student["passed"])

    if missing_subjects:
        reasons.append(f"Missing required subject(s): {missing_subjects}")


    is_eligible = len(reasons) == 0

    return is_eligible, reasons
        


def forward_chaining(known_facts, courses):
    # return list of courses dict
        # name: str, 
        # is_eligible: bool, 
        # reasons: list[], 
        # perference_match: {fav_subj: bool, career_goal: bool}

    soft_key = ["fav_subject", "career_goal"]
    results = []

    # student facts about hard requirements
    stu_hard = {"credits": temp_facts["credits"],
                "passed": []}

    for key in ("passed_math", "passed_science"):
        if known_facts[key] == True:
            stu_hard["passed"].append(key)

    # student facts about soft perferences
    stu_soft = {key: known_facts.get(key) for key in ("fav_subject", "career_goal")}


    for course in courses:
        # check if eligible + return reasons
        is_eligible, reasons = check_eligible(stu_hard, course["hard"])

        # match perferences
        perf_match = {}

        for key in soft_key:
            perf_match[key] = stu_soft[key] == course["soft"][key]

            # add new reasons
            if perf_match[key]:
                reasons.append(f"{key} Matched")

        # add result of each course
        results.append({
            "name": course["name"],
            "eligible": is_eligible,
            "reasons": reasons,
            "perf_match": perf_match
        })

    return results




if __name__ == "__main__":
    courses = load_courses()

    temp_facts = {
        "name" : "John",
        "credits": 45,
        "passed_math": True,
        "passed_science": True,
        "fav_subject": "computing",
        "career_goal": "software"
    }


    results = forward_chaining(temp_facts, courses)
    for res in results:
        print(res["Name"], res["Eligible"], res["Reasons"])

