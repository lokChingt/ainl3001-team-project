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


def calculate_score(perf_match):
    """
    input: perf_match: dictionary of perferenced in boolean
    return: score: int
    """

    score = 0
    
    if perf_match["fav_subject"]:
        score += 2
    
    if perf_match["career_goal"]:
        score += 1

    return score


def rank_courses(results):
    """
    input: results: list of course dictionary)
    return: ranked_course: list of eligible course dictionary
    """

    eligible_courses = [course for course in results if course["eligible"]]

    # calculate scores
    for course in eligible_courses:
        course["match_score"] = calculate_score(course["perf_match"])

    # sort by score
    ranked_courses = sorted(eligible_courses, key=lambda course: (-course["match_score"], course["name"]))

    # add ranking
    for i, course in enumerate(ranked_courses):
        course["rank"] = i + 1

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

    for course in courses:
        known_facts = build_initial_facts(temp_facts, course)

        all_rules = load_rules()
        rules = get_course_rules(all_rules, course["_id"])

        inferred_facts, triggered_rules = forward_chaining(known_facts, rules)
        print(inferred_facts)