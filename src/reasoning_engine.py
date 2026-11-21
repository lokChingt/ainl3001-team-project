from loader import load_courses
from knowledge_base import load_rules, get_course_rules

def build_initial_facts(known_facts, course):
    course_id = course["_id"]

    facts = set()

    # check hard requirement (credits, passed subjects)
    if known_facts["credits"] >= course["hard"]["min_credits"]:
        facts.add(f"credits_sufficient:{course_id}")

    passed_subjects = set(known_facts.get("passed_subjects", []))
    required_subjects = set(course["hard"]["requires"])

    if required_subjects.issubset(passed_subjects):
        facts.add(f"required_subjects_met:{course_id}")


    # check soft perference (favourite subject, career goal)
    stu_fav_subject = known_facts.get("fav_subject")
    course_fav_subject = course["soft"].get("fav_subject")

    if stu_fav_subject is not None and course_fav_subject is not None:
        if stu_fav_subject == course_fav_subject:
            facts.add(f"fav_subject_match:{course_id}")

    stu_career_goal = known_facts.get("career_goal")
    course_career_goal = course["soft"].get("career_goal")

    if stu_career_goal is not None and course_career_goal is not None:
            if stu_career_goal == course_career_goal:
                facts.add(f"career_goal_match:{course_id}")

    return facts


def forward_chaining(known_facts, rules):
    inferred_facts = set(known_facts)
    triggered_rules = []
    triggered_rule_idx = set()
    changed = True


    while changed:
        changed = False

        for rule in rules:
            rule_id = rule["id"]
            conditions = rule["conditions"]
            conclusion = rule["conclusion"]

            # check if all conditions are known
            if all(condition in inferred_facts for condition in conditions):

                # prevent duplicate rule triggered
                if rule_id not in triggered_rule_idx:
                    triggered_rule_idx.add(rule_id)

                    triggered_rules.append({
                        "rule_id": rule_id,
                        "conditions": conditions,
                        "conclusion": conclusion
                    })

                # add new fact if not already exist
                if conclusion not in inferred_facts:
                    inferred_facts.add(conclusion)
                    changed = True

    return inferred_facts, triggered_rules


def calculate_score(triggered_rules, all_rules):
    """
    input:
        triggered_rules: list of dictionary
        all_rules: list of dictionary
    return: score: int
    """

    score = 0

    # get score from each rules
    rule_scores = {
        rule["id"]: rule.get("score", 0)
        for rule in all_rules
    }

    # calculate score based on triggered rules
    for rule in triggered_rules:
        rule_id = rule["rule_id"]
        score += rule_scores.get(rule_id, 0)

    return score


def rank_courses(results):
    """
    input: results: list of course dictionary
    return: 
        ranked_courses: list of eligible course dictionary
        ineligible_courses: list of ineligible course dictionary
    """

    eligible_courses = [course for course in results if course["is_eligible"]]
    ineligible_courses = [course for course in results if not course["is_eligible"]]

    # sort by score
    ranked_courses = sorted(eligible_courses, key=lambda course: (-course["score"], course["name"]))

    # add ranking
    for rank, course in enumerate(ranked_courses, start=1):
        course["rank"] = rank

    return ranked_courses, ineligible_courses


def get_course_reasons(triggered_rules):
    reasons = set()

    # get reason for each applied rules
    for rule in triggered_rules:
        rule_id = rule["rule_id"]

        match rule_id:
            case "R1":
                reason = "Meet all requirements"
            case "R2":
                reason = "Match subject perference"
            case "R3":
                reason = "Match career goal"

        reasons.add(reason)

    return reasons


def get_ineligible_reasons(student, course):
    reasons = []

    required_credits = course["hard"]["min_credits"]

    # check if insufficient credits
    if student["credits"] < required_credits:
        reasons.append(f"Insufficient credits: {student['credits']} completed, {required_credits} required")


    passed_subjects = set(student.get("passed_subjects", []))
    required_subjects = set(course["hard"]["requires"])

    missing_subjects = required_subjects - passed_subjects

    # check if missing subjects
    if missing_subjects:
        subjects = ", ".join(missing_subjects)
        reasons.append(f"Missing subjects {subjects}")

    return reasons


def evaluate_courses(known_facts, courses, all_rules):
    """
    input:
        known_facts: dictionary
        courses: list of dictionary
        all_rules: list of dictionary
    return:
        ranked_courses: list of dictionary
        ineligible_courses: list of dictionary
    """

    results = []

    for course in courses:
        # build initial facts + course rules
        initial_facts = build_initial_facts(known_facts, course)
        rules = get_course_rules(all_rules, course["_id"])

        # forward chaining
        inferred_facts, triggered_rules = forward_chaining(initial_facts, rules)

        # check if eligible
        is_eligible = (f"eligible:{course["_id"]}" in inferred_facts)

        # calculate score + get reasons
        if is_eligible:
            score = calculate_score(triggered_rules, all_rules)
            reasons = get_course_reasons(triggered_rules)
        else:
            score = 0
            reasons = get_ineligible_reasons(known_facts, course)

        # store each course result
        results.append({
            "id": course["_id"],
            "name": course["name"],
            "is_eligible": is_eligible,
            "score": score,
            "reasons": reasons
        })

    # rank courses
    ranked_courses = rank_courses(results)

    return ranked_courses



if __name__ == "__main__":
    courses = load_courses()

    temp_facts = {
        "name" : "John",
        "credits": 45,
        "passed_subjects": ["math", "science"],
        "fav_subject": "computing",
        "career_goal": "software"
    }

    all_rules = load_rules()

    ranked_courses, ineligible_courses = evaluate_courses(temp_facts, courses, all_rules)

    # display Recommended Courses
    print("\n--------- Recommended Courses ----------")
    print(f"\n{'Rank':<3} | {'Course Name':<15} | {'Score':<5} | {'Explanation'}")
    print("-" * 100)

    for course in ranked_courses:
        reasons = ", ".join(course["reasons"])

        print(
            f"{course['rank']:<6}"
            f"{course['name']:<20}"
            f"{course['score']:<7}"
            f"{reasons}"
        )

    # display Ineligible Courses
    print("\n--------- Ineligible Courses ----------")
    print(f"\n{'Course Name':<15} | {'Explanation'}")
    print("-" * 70)

    for course in ineligible_courses:
        reasons = ", ".join(course["reasons"])
        
        print(
            f"{course['name']:<17}"
            f"{reasons}"
        )
