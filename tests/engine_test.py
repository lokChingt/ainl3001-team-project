import sys
from pathlib import Path
import unittest

# import loader.py from project roots
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from reasoning_engine import (
    build_initial_facts,
    forward_chaining,
    calculate_score,
    rank_courses,
    get_course_reasons,
    get_ineligible_reasons,
    evaluate_courses
)

# =============== build_initial_facts Test Cases (9) ================
class TestBuildInitialFacts(unittest.TestCase):
    def setUp(self):
        self.student = {
            "credits": 60,
            "passed_subjects": ["math", "science"],
            "fav_subject": "maths",
            "career_goal": "software"
        }

        self.course = {
            "_id": "C1",
            "name": "Engineering",
            "hard": {
                "min_credits": 50, 
                "requires": ["math"]
            },
            "soft": {
                "fav_subject": "maths", 
                "career_goal": "software"
            }
        }

    # -------- test credit -------------
    def test_sufficient_credits(self):
        facts = build_initial_facts(self.student, self.course)
        self.assertIn(f"credits_sufficient:{self.course["_id"]}", facts)

    def test_exact_sufficient_credits(self):
        student = self.student.copy()
        student["credits"] = self.course["hard"]["min_credits"]

        facts = build_initial_facts(student, self.course)
        self.assertIn(f"credits_sufficient:{self.course["_id"]}", facts)

    def test_insufficient_credits(self):
        student = self.student.copy()
        student["credits"] = self.course["hard"]["min_credits"] - 10

        facts = build_initial_facts(student, self.course)
        self.assertNotIn(f"credits_sufficient:{self.course["_id"]}", facts)


    # -------- test required subjects -------------
    def test_requires_met(self):
        facts = build_initial_facts(self.student, self.course)
        self.assertIn(f"required_subjects_met:{self.course["_id"]}", facts)

    def test_requires_not_met(self):
        self.student["passed_subjects"] = ["science"]
        facts = build_initial_facts(self.student, self.course)
        self.assertNotIn(f"required_subjects_met:{self.course["_id"]}", facts)


    # -------- test favourite subject -------------
    def test_fav_subject_met(self):
        facts = build_initial_facts(self.student, self.course)
        self.assertIn(f"fav_subject_match:{self.course["_id"]}", facts)

    def test_fav_subject_not_met(self):
        self.student["fav_subject"] = "science"
        facts = build_initial_facts(self.student, self.course)
        self.assertNotIn(f"fav_subject_match:{self.course["_id"]}", facts)


    # -------- test career goal -------------
    def test_career_goal_met(self):
        facts = build_initial_facts(self.student, self.course)
        self.assertIn(f"career_goal_match:{self.course["_id"]}", facts)

    def test_career_goal_not_met(self):
        self.student["career_goal"] = "health"
        facts = build_initial_facts(self.student, self.course)
        self.assertNotIn(f"career_goal_match:{self.course["_id"]}", facts)


# =============== foward_chaining Test Cases (7) ================
class TestForwardChaining(unittest.TestCase):
    def setUp(self):
        self.course_id = "C1"

        self.rules = [
            {
                "id": "R1",
                "conditions": [
                    f"credits_sufficient:{self.course_id}",
                    f"required_subjects_met:{self.course_id}"
                ],
                "conclusion": f"eligible:{self.course_id}"
            },
            {
                "id": "R2",
                "conditions": [
                    f"eligible:{self.course_id}",
                    f"fav_subject_match:{self.course_id}"
                ],
                "conclusion": f"subject_preference_matched:{self.course_id}"
            },
            {
                "id": "R3",
                "conditions": [
                    f"eligible:{self.course_id}",
                    f"career_goal_match:{self.course_id}"
                ],
                "conclusion": f"career_preference_matched:{self.course_id}"
            },
            {
                "id": "R4",
                "conditions": [
                    f"eligible:{self.course_id}",
                    f"subject_preference_matched:{self.course_id}"
                ],
                "conclusion": f"recommended:{self.course_id}"
            },
            {
                "id": "R5",
                "conditions": [
                    f"eligible:{self.course_id}",
                    f"career_preference_matched:{self.course_id}"
                ],
                "conclusion": f"recommended:{self.course_id}"
            },
            {
                "id": "R6",
                "conditions": [
                    f"eligible:{self.course_id}",
                    f"subject_preference_matched:{self.course_id}",
                    f"career_preference_matched:{self.course_id}"
                ],
                "conclusion": f"strong_recommendation:{self.course_id}"
            }
        ]

    # a little helper for checking if the triggered rules are what expected
    def assert_triggered_rules(self, triggered_rules, expected_ids):
        actual_ids = {rule["rule_id"] for rule in triggered_rules}
        self.assertEqual(actual_ids, expected_ids)


    # Only have test cases for R4-6 because these rules will trigger R1-3,
    # which could test those rules at the same time
    def test_r4_subject_recommandation(self):
        known_facts = {
            f"credits_sufficient:{self.course_id}",
            f"required_subjects_met:{self.course_id}",
            f"fav_subject_match:{self.course_id}"
        }

        inferred_facts, triggered_rules = forward_chaining(known_facts, self.rules)

        expected_ids = {"R1", "R2", "R4"}

        self.assertIn(f"recommended:{self.course_id}", inferred_facts)
        self.assert_triggered_rules(triggered_rules, expected_ids)


    def test_r5_career_recommendation(self):
        known_facts = {
            f"credits_sufficient:{self.course_id}",
            f"required_subjects_met:{self.course_id}",
            f"career_goal_match:{self.course_id}"
        }

        inferred_facts, triggered_rules = forward_chaining(known_facts, self.rules)

        expected_ids = {"R1", "R3", "R5"}

        self.assertIn(f"recommended:{self.course_id}", inferred_facts)
        self.assert_triggered_rules(triggered_rules, expected_ids)

    def test_r6_strong_recommendation(self):
        known_facts = {
            f"credits_sufficient:{self.course_id}",
            f"required_subjects_met:{self.course_id}",
            f"fav_subject_match:{self.course_id}",
            f"career_goal_match:{self.course_id}"
        }

        inferred_facts, triggered_rules = forward_chaining(known_facts, self.rules)

        expected_ids = {"R1", "R2", "R3", "R4", "R5", "R6"}
        
        self.assertIn(f"strong_recommendation:{self.course_id}", inferred_facts)
        self.assert_triggered_rules(triggered_rules, expected_ids)
    
    
    # Test cases for missing credits and missing required subjects
    def test_missing_credits(self):
        known_facts = {
            f"required_subjects_met:{self.course_id}"
        }

        inferred_facts, triggered_rules = forward_chaining(known_facts, self.rules)

        self.assertNotIn(f"eligible:{self.course_id}", inferred_facts)
        self.assertEqual(inferred_facts, known_facts)
        self.assertEqual(triggered_rules, [])


    def test_missing_required_subjects(self):
        known_facts = {
            f"credits_sufficient:{self.course_id}"
        }

        inferred_facts, triggered_rules = forward_chaining(known_facts, self.rules)

        self.assertNotIn(f"eligible:{self.course_id}", inferred_facts)
        self.assertEqual(inferred_facts, known_facts)
        self.assertEqual(triggered_rules, [])


    # Test cases for empty facts and empty rules
    def test_empty_known_facts(self):
        known_facts = {}

        inferred_facts, triggered_rules = forward_chaining(known_facts, self.rules)

        self.assertEqual(inferred_facts, set())
        self.assertEqual(triggered_rules, [])


    def test_empty_rules(self):
        known_facts = {
            f"credits_sufficient:{self.course_id}",
            f"required_subjects_met:{self.course_id}"
        }

        self.rules = []

        inferred_facts, triggered_rules = forward_chaining(known_facts, self.rules)

        self.assertEqual(inferred_facts, known_facts)
        self.assertEqual(triggered_rules, [])


# =============== calculate_score Test Cases (6) ================
class TestCalculateScore(unittest.TestCase):
    def setUp(self):
        self.all_rules = [
            {"id": "R2", "score": 2},
            {"id": "R3", "score": 1}
        ]

    # check score with only one rule triggered
    def test_single_rule_score(self):
        triggered_rules = [
            {"rule_id": "R2"}
        ]

        score = calculate_score(triggered_rules, self.all_rules)

        self.assertEqual(score, 2)

    # check score with multiple rules triggered
    def test_multiple_rule_score(self):
        triggered_rules = [
            {"rule_id": "R2"},
            {"rule_id": "R3"}
        ]

        score = calculate_score(triggered_rules, self.all_rules)

        self.assertEqual(score, 3)

    # # check score with no rule triggered
    def test_empty_triggered_rules(self):
        triggered_rules = []

        score = calculate_score(triggered_rules, self.all_rules)

        self.assertEqual(score, 0)

    # check score with rules triggered have no score
    def test_no_scoring_rules(self):
        triggered_rules = [
            {"rule_id": "R1"},
            {"rule_id": "R4"}
        ]

        score = calculate_score(triggered_rules, self.all_rules)

        self.assertEqual(score, 0)

    # check score with unknown rule triggered
    def test_unknown_rule_id(self):
        triggered_rules = [
            {"rule_id": "R100"}
        ]

        score = calculate_score(triggered_rules, self.all_rules)

        self.assertEqual(score, 0)


# =============== rank_courses Test Cases (4) ================
class TestRankCourses(unittest.TestCase):
    def setUp(self):
        self.results = [
            {
                "_id": "C1",
                "name": "Engineering",
                "is_eligible": False,
                "score": 0
            },
            {
                "_id": "C2",
                "name": "Computer Science",
                "is_eligible": True,
                "score": 3
            },
            {
                "_id": "C4",
                "name": "Geography",
                "is_eligible": True,
                "score": 0
            },
            {
                "_id": "C5",
                "name": "English",
                "is_eligible": False,
                "score": 0
            },
            {
                "_id": "C6",
                "name": "Data Science",
                "is_eligible": True,
                "score": 2
            },
            {
                "_id": "C7",
                "name": "Biology",
                "is_eligible": True,
                "score": 0
            }
        ]

    # check sorting, ranking, ineligible course
    def test_rank_courses(self):
        ranked_courses, ineligible_courses = rank_courses(self.results)

        # check sorting by score and alphabetical order
        self.assertEqual(
            [c["name"] for c in ranked_courses],
            [
                "Computer Science",
                "Data Science",
                "Biology",
                "Geography"
            ]
        )

        # check ranking
        self.assertEqual(
            [c["rank"] for c in ranked_courses],
            [1, 2, 3, 4]
        )

        # check ineligible courses
        self.assertEqual(
            [c["name"] for c in ineligible_courses],
            [
                "Engineering",
                "English"
            ]
        )

        # check ineligible courses don't have ranking
        self.assertNotIn("rank", ineligible_courses[0])

    # test when all courses are ineligible
    def test_no_eligible_courses(self):
        self.results = [
            {
                "_id": "C1",
                "name": "Engineering",
                "is_eligible": False,
                "score": 0
            },
            {
                "_id": "C5",
                "name": "English",
                "is_eligible": False,
                "score": 0
            }
        ]
        ranked_courses, ineligible_courses = rank_courses(self.results)

        self.assertEqual(ranked_courses, [])
        self.assertEqual(len(ineligible_courses), 2)

    # test when all courses are eligible
    def test_all_eligible_courses(self):
        self.results = [
            {
                "_id": "C2",
                "name": "Computer Science",
                "is_eligible": True,
                "score": 3
            },
            {
                "_id": "C4",
                "name": "Geography",
                "is_eligible": True,
                "score": 0
            }
        ]
        ranked_courses, ineligible_courses = rank_courses(self.results)

        self.assertEqual(len(ranked_courses), 2)
        self.assertEqual(ineligible_courses, [])

    # test when empty course results
    def test_empty_results(self):
        self.results = []

        ranked_courses, ineligible_courses = rank_courses(self.results)

        self.assertEqual(ranked_courses, [])
        self.assertEqual(ineligible_courses, [])


# =============== get_course_reasons Test Cases (3) ================
class TestGetCourseReasons(unittest.TestCase):
    def test_get_course_reasons(self):
        triggered_rules = [
            {"rule_id": "R1"},
            {"rule_id": "R2"},
            {"rule_id": "R3"}
        ]

        reasons = get_course_reasons(triggered_rules)

        self.assertEqual(len(reasons), 3)
        self.assertIn("Meet all requirements", reasons)
        self.assertIn("Match subject preference", reasons)
        self.assertIn("Match career goal", reasons)

    # test if no rule triggered
    # expect: no reasons
    def test_empty_triggered_rules(self):
        triggered_rules = []

        reasons = get_course_reasons(triggered_rules)

        self.assertEqual(reasons, [])

    # test if unknown rule id
    # expect: no reasons
    def test_unknown_rule_id(self):
        triggered_rules = [
            {"rule_id": "R100"}
        ]

        reasons = get_course_reasons(triggered_rules)
        
        self.assertEqual(reasons, [])


# =============== get_ineligible_reasons Test Cases (3) ================
class TestGetIneligibleReasons(unittest.TestCase):
    def setUp(self):
        self.student = {
            "credits": 60,
            "passed_subjects": ["math", "science"]
        }

        self.course = {
            "_id": "C1",
            "name": "Engineering",
            "hard": {
                "min_credits": 50, 
                "requires": ["math"]
            }
        }

    # check if insufficient credits
    def test_insufficient_credits(self):
        student = self.student.copy()
        student["credits"] = self.course["hard"]["min_credits"] - 10

        reasons = get_ineligible_reasons(student, self.course)

        self.assertEqual(len(reasons), 1)
        self.assertIn("Insufficient credits", reasons[0])

    # check if missing required subject
    def test_missing_required_subjects(self):
        student = self.student.copy()
        required_subject = self.course["hard"]["requires"][0]
        student["passed_subjects"].remove(required_subject)

        reasons = get_ineligible_reasons(student, self.course)

        self.assertEqual(len(reasons), 1)
        self.assertIn("Missing subjects", reasons[0])

    # check if insufficient credits and missing required subjects
    def test_multiple_ineligible_reasons(self):
        student = {
            "credits": 40,
            "passed_subjects": ["science"]
        }

        reasons = get_ineligible_reasons(student, self.course)

        self.assertEqual(len(reasons), 2)
        self.assertIn("Insufficient credits", reasons[0])
        self.assertIn("Missing subjects", reasons[1])
    

# =============== evaluate_courses Test Cases (3) ================
class TestEvaluateCourses(unittest.TestCase):
    def setUp(self):
        self.known_facts = {
            "credits": 45,
            "passed_subjects": ["math", "science"],
            "fav_subject": "computing",
            "career_goal": "software"
        }

        self.courses = [
            {
                "_id": "C2",
                "name": "Computer Science",
                "hard": {
                    "min_credits": 40, 
                    "requires": ["math"]
                },
                "soft": {
                    "fav_subject": "computing", 
                    "career_goal": "software"
                }
            },
            {
                "_id": "C12",
                "name": "Law",
                "hard": {
                    "min_credits": 50, 
                    "requires": []
                },
                "soft": {
                    "fav_subject": "languages", 
                    "career_goal": "law"
                }
            }
        ]

        self.all_rules = [
            {
                "id": "R1",
                "conditions": [
                    "credits_sufficient:{course_id}",
                    "required_subjects_met:{course_id}"
                ],
                "conclusion": "eligible:{course_id}"
            },
            {
                "id": "R2",
                "conditions": [
                    "eligible:{course_id}",
                    "fav_subject_match:{course_id}"
                ],
                "conclusion": "subject_preference_matched:{course_id}",
                "score": 2
            },
            {
                "id": "R3",
                "conditions": [
                    "eligible:{course_id}",
                    "career_goal_match:{course_id}"
                ],
                "conclusion": "career_preference_matched:{course_id}",
                "score": 1
            },
            {
                "id": "R4",
                "conditions": [
                    "eligible:{course_id}",
                    "subject_preference_matched:{course_id}"
                ],
                "conclusion": "recommended:{course_id}"
            },
            {
                "id": "R5",
                "conditions": [
                    "eligible:{course_id}",
                    "career_preference_matched:{course_id}"
                ],
                "conclusion": "recommended:{course_id}"
            },
            {
                "id": "R6",
                "conditions": [
                    "eligible:{course_id}",
                    "subject_preference_matched:{course_id}",
                    "career_preference_matched:{course_id}"
                ],
                "conclusion": "strong_recommendation:{course_id}"
            }
        ]

    # check eligible courses, score, reasons, ineligible courses
    def test_evaluate_courses(self):
        ranked_courses, ineligible_courses = evaluate_courses(
            self.known_facts, self.courses, self.all_rules
        )

        # check eligible course
        self.assertEqual(len(ranked_courses), 1)
        self.assertEqual(ranked_courses[0]["id"], "C2")
        self.assertTrue(ranked_courses[0]["is_eligible"])

        # check score
        self.assertEqual(ranked_courses[0]["score"], 3)

        # check reasons
        self.assertIn(
            "Meet all requirements",
            ranked_courses[0]["reasons"]
        )
        self.assertIn(
            "Match subject preference",
            ranked_courses[0]["reasons"]
        )
        self.assertIn(
            "Match career goal",
            ranked_courses[0]["reasons"]
        )

        # check ineligible course
        self.assertEqual(len(ineligible_courses), 1)
        self.assertEqual(ineligible_courses[0]["id"], "C12")
        self.assertFalse(ineligible_courses[0]["is_eligible"])


    # test if empty courses list
    def test_evaluate_no_courses(self):
        ranked_courses, ineligible_courses = evaluate_courses(
            self.known_facts, [], self.all_rules
        )

        self.assertEqual(ranked_courses, [])
        self.assertEqual(ineligible_courses, [])

    # test if all courses are ineligible
    def test_evaluate_all_ineligible_courses(self):
        courses = [
            {
                "_id": "C11",
                "name": "Medicine",
                "hard": {
                    "min_credits": 55, 
                    "requires": ["math", "science"]
                },
                "soft": {
                    "fav_subject": "science", 
                    "career_goal": "health"
                }
            },
            {
                "_id": "C12",
                "name": "Law",
                "hard": {
                    "min_credits": 50, 
                    "requires": []
                },
                "soft": {
                    "fav_subject": "languages", 
                    "career_goal": "law"
                }
            }
        ]

        ranked_courses, ineligible_courses = evaluate_courses(
            self.known_facts, courses, self.all_rules
        )

        self.assertEqual(ranked_courses, [])
        self.assertEqual(len(ineligible_courses), 2)



if __name__ == "__main__":
    unittest.main()