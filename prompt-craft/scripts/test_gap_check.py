#!/usr/bin/env python3
"""最小自我檢查（assert-based，非測試框架）。跑法：
    python3 scripts/test_gap_check.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gap_check import contains_term, detect_dimensions, load_json  # noqa: E402


def test_contains_term_word_boundary():
    assert contains_term("I want a formal tone", "tone") is True
    assert contains_term("faster", "as a") is False
    assert contains_term("請以主管的身分回覆", "身分") is True


def test_wish_type_request_misses_everything():
    gap_keywords = load_json("gap_keywords.json")
    detected, missing = detect_dimensions("幫我寫封信", gap_keywords)
    assert detected == []
    assert {m["key"] for m in missing} == {
        "role", "context", "format", "audience_tone", "example", "constraints_steps"
    }


def test_well_specified_request_detects_most_dimensions():
    gap_keywords = load_json("gap_keywords.json")
    text = (
        "請你以行政助理的身分，用正式語氣寫一封信給主管請假，"
        "格式維持在200字以內，附一個範例段落當參考。"
    )
    detected, missing = detect_dimensions(text, gap_keywords)
    detected_keys = {d["key"] for d in detected}
    assert {"role", "audience_tone", "format", "example"} <= detected_keys
    assert "constraints_steps" in {m["key"] for m in missing}


def run_all():
    tests = [
        test_contains_term_word_boundary,
        test_wish_type_request_misses_everything,
        test_well_specified_request_detects_most_dimensions,
    ]
    for t in tests:
        t()
        print(f"  ok: {t.__name__}")
    print("all tests passed")


if __name__ == "__main__":
    run_all()
