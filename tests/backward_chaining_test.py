import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/ "src"))

from main import backward_chaining

def rule(rule_id, conditions, conclusion):
    return{"id": rule_id, "conditions": conditions, "conclusion": conclusion}

# goal already in known facts
def test_known_fact():
    assert backward_chaining("math", {"math"}, [], []) is True

# all conditions met -> proven and rule recorded
def test_rule_proven():
    rules = [rule("R1", ["credits_40", "math"], "eligible:cs")]
    triggered = []
    assert backward_chaining("eligible:cs", {"credits_40", "math"}, rules, triggered) is True
    assert [r["rule_id"] for r in triggered] == ["R1"]

# one codition missing -> not proven, nothing recorded
def test_rule_not_proven():
    rules = [rule("R1", ["credits_40", "math"], "eligible:cs")]
    triggered = []
    assert backward_chaining("eligible:cs", {"credits_40"}, rules, triggered) is False
    assert triggered == []

# goal depends on a sub-goal proven by another rule
def test_chain():
    rules = [rule("R1", ["math"], "meet_reqs:cs"), rule("R2", ["meet_reqs:cs"], "eligible:cs"),]
    triggered = []
    assert backward_chaining("eligible:cs", {"math"}, rules, triggered) is True
    assert [r["rule_id"] for r in triggered] == ["R1", "R2"]