#!/usr/bin/env python3
"""最小自我檢查（assert-based，非測試框架）。跑法：
    python3 scripts/test_profile_check.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile_check import contains_term, detect_hits, detect_identity_only, load_json  # noqa: E402


def test_empty_adjective_hit():
    cliche_data = load_json("cliche_phrases.json")
    text = "熱愛生活，個性隨和，希望遇到聊得來的人"
    hits = detect_hits(text, cliche_data["empty_adjectives"])
    assert "熱愛生活" in hits
    assert "個性隨和" in hits
    assert "希望遇到聊得來的人" in hits


def test_generic_interest_kept_separate_from_empty_adjective():
    cliche_data = load_json("cliche_phrases.json")
    text = "喜歡旅行、美食、看電影，上個月自己一個人跑去花蓮玩"
    empty_hits = detect_hits(text, cliche_data["empty_adjectives"])
    interest_hits = detect_hits(text, cliche_data["generic_interest_categories"])
    assert empty_hits == []
    assert set(interest_hits) == {"旅行", "美食", "看電影"}


def test_identity_only_true_for_bare_tag():
    cliche_data = load_json("cliche_phrases.json")
    text = "不太會介紹自己，工作是行銷，平常沒事就滑手機，看緣分吧。"
    char_count = len(re.sub(r"\s+", "", text))
    empty_hits = detect_hits(text, cliche_data["empty_adjectives"])
    interest_hits = detect_hits(text, cliche_data["generic_interest_categories"])
    # 這句其實命中「看緣分」類的空話，不算純身份標籤，用來驗證『有命中就不是 identity_only』
    assert detect_identity_only(text, char_count, cliche_data, empty_hits, interest_hits) is False

    bare_text = "24y 研究生"
    bare_char_count = len(re.sub(r"\s+", "", bare_text))
    bare_empty_hits = detect_hits(bare_text, cliche_data["empty_adjectives"])
    bare_interest_hits = detect_hits(bare_text, cliche_data["generic_interest_categories"])
    assert detect_identity_only(
        bare_text, bare_char_count, cliche_data, bare_empty_hits, bare_interest_hits
    ) is True


def test_identity_only_false_when_content_exists():
    cliche_data = load_json("cliche_phrases.json")
    text = "平常玩樂團，在Livehouse圈小有名氣，之前也練過拳擊。"
    char_count = len(re.sub(r"\s+", "", text))
    empty_hits = detect_hits(text, cliche_data["empty_adjectives"])
    interest_hits = detect_hits(text, cliche_data["generic_interest_categories"])
    assert detect_identity_only(text, char_count, cliche_data, empty_hits, interest_hits) is False


def test_contains_term_basic():
    assert contains_term("熱愛生活的人", "熱愛生活") is True
    assert contains_term("認真工作", "熱愛生活") is False


def run_all():
    tests = [
        test_empty_adjective_hit,
        test_generic_interest_kept_separate_from_empty_adjective,
        test_identity_only_true_for_bare_tag,
        test_identity_only_false_when_content_exists,
        test_contains_term_basic,
    ]
    for t in tests:
        t()
        print(f"  ok: {t.__name__}")
    print("all tests passed")


if __name__ == "__main__":
    run_all()
