import json
import sys
from pathlib import Path
import pytest

# import loader.py from project roots
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from knowledge_base import load_courses

REAL_FILE = ROOT / "data" / "course.json"

# write copy of rules file to not interfer with original one
def make_file(tmp_path, courses):
    path = tmp_path / "rules.json"
    path.write_text(json.dumps({"courses":courses}), encoding="utf-8")
    return path

# valid course
def good_course():
    return{
        "name": "Test Course",
        "hard": {"min_credits": 40, "requires": ["passed_math"]},
        "soft": {"fav_subject": "Computing", "career_goal": "Software"}
    }

#================= test on course.json ============================

# load without errors and has at least 10 courses
def test_real_file_loads():
    assert len(load_courses(REAL_FILE)) >= 10

# check every course is unique
def test_names_unique():
    names = [c["name"] for c in load_courses(REAL_FILE)]
    assert len(names) == len(set(names))

# check known values to ensure no changes
def test_known_values():
    by_name = {c["name"]: c for c in load_courses(REAL_FILE)}
    assert by_name["Engineering"]["hard"]["min_credits"] == 50
    assert by_name["Computer Science"]["hard"]["requires"] == ["passed_math"]


#=============== test loading and normalization =====================

# check valid course defination with loading errors
def test_valid_course_loads(tmp_path):
    courses = load_courses(make_file(tmp_path, [good_course()]))
    assert courses[0]["name"] == "Test Course"

# perferneces should be lowecase
def test_text_lowercase(tmp_path):
    c = load_courses(make_file(tmp_path, [good_course()]))[0]
    assert c["soft"]["fav_subject"] == "computing"
    assert c["soft"]["career_goal"] == "software"


#============ Test invalid inputs ==============================

# caheck non-existent file should output error
def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_courses(tmp_path/ "nope.json")

# invalid JSON should raise error
def test_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_courses(path)

# test empty course list
def test_no_courses(tmp_path):
    with pytest.raises(ValueError):
        load_courses(make_file(tmp_path, []))

# course must have name field
def test_missing_name(tmp_path):
    course = good_course()
    del course["name"]
    with pytest.raises(ValueError):
        load_courses(make_file(tmp_path, [course]))

# duplicare course name not allowed
def test_duplicate_name(tmp_path):
    with pytest.raises(ValueError):
        load_courses(make_file(tmp_path, [good_course(), good_course()]))

# credits can't be negative
def test_negative_credits(tmp_path):
    course = good_course()
    course["hard"]["min_credits"] = -5
    with pytest.raises(ValueError):
        load_courses(make_file(tmp_path, [course]))

# facts must be in set
def test_unknown_facts(tmp_path):
    course = good_course()
    course["hard"]["requires"] = ["passed_art"]
    with pytest.raises(ValueError):
        load_courses(make_file(tmp_path, [course]))