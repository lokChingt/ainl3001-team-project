import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from student_input import load_students
from knowledge_base import load_courses, load_rules
from reasoning_engine import evaluate_courses

# expected results worked out by hand 
EXPECTED = {
    "John":  ("Computer Science", 12),
    "Aoife": ("Medicine", 12),
    "Liam":  ("Business", 3),
    "Sofia": ("Law", 8),
    "Tomas": ("Data Science", 6),
    "Petr":  ("Computer Science", 4),
    "Eva":   ("Psychology", 2),
    "Finn":  ("Chemistry", 12),
    "Grace": ("Geography", 2),
    "Hugo":  ("Physics", 9),
}

STUDENTS = {s["name"]: s for s in load_students()}
COURSES = load_courses()
RULES = load_rules()

def run(name):
    """run 1 sample student through the whole system"""
    return evaluate_courses(STUDENTS[name], COURSES, RULES)

@pytest.mark.parametrize("name", EXPECTED)
def test_best_course_and_eligible_count(name):
    best, count = EXPECTED[name]
    ranked, ineligible = run(name)
    assert ranked[0]["name"] == best
    assert len(ranked) == count
    assert len(ranked) + len(ineligible) == 12

def test_exactly_on_minimum_counts():
    ranked, _ = run("Petr")
    assert STUDENTS["Petr"]["credits"] == 40
    assert ranked[0]["name"] == "Computer Science"
    ranked, _ = run("Eva")
    assert STUDENTS["Eva"]["credits"] == 35
    assert ranked[0]["name"] == "Psychology"

def test_hugo_medicine_blocked():
    ranked, ineligible = run("Hugo")
    assert ranked[0]["name"] == "Physics"
    assert "Medicine" in [c["name"] for c in ineligible]

def test_grace_no_preference_match():
    ranked, _ = run("Grace")
    assert ranked[0]["name"] == "Geography"
    assert ranked[0]["score"] == 0

def test_finn_tie_alphabetical():
    ranked, _ = run("Finn")
    assert [c["name"] for c in ranked[:2]] == ["Chemistry", "Physics"]
    assert ranked[0]["score"] == ranked[1]["score"] == 3
