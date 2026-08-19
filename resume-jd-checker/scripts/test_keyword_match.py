#!/usr/bin/env python3
"""最小自我檢查（assert-based，非測試框架）。跑法：
    python3 scripts/test_keyword_match.py
全部 assert 通過會印 "all tests passed"，任何一條斷言失敗會直接丟例外中止。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from keyword_match import (  # noqa: E402
    contains_term,
    build_synonym_lookup,
    expand_terms,
    match_keywords,
    scan_ai_tell,
    load_json,
)


def test_contains_term_word_boundary():
    assert contains_term("I used Docker and Kubernetes", "Docker") is True
    assert contains_term("email me anytime", "AI") is False  # 短詞不誤判子字串
    assert contains_term("我熟悉 AI 相關技術", "AI") is True


def test_bilingual_synonym_match():
    synonyms = {"retrieval-augmented generation": ["檢索增強生成", "RAG"]}
    lookup = build_synonym_lookup(synonyms)
    terms = expand_terms("RAG", lookup)
    assert "檢索增強生成" in terms
    assert "RAG" in terms

    resume = "曾建置檢索增強生成系統，整合向量資料庫。"
    jd = "熟悉 RAG 架構者優先。"
    matched, missing = match_keywords(resume, jd, ["RAG"], lookup)
    assert matched == ["RAG"], f"expected RAG matched via 中文同義詞, got {matched}"
    assert missing == []


def test_missing_keyword_detected():
    synonyms = {}
    lookup = build_synonym_lookup(synonyms)
    resume = "負責前端開發，使用 React。"
    jd = "需要熟悉 Kubernetes 與 Docker 的候選人。"
    matched, missing = match_keywords(resume, jd, ["Kubernetes", "Docker"], lookup)
    assert set(missing) == {"Kubernetes", "Docker"}
    assert matched == []


def test_ai_tell_detection():
    ai_tell = load_json("ai_tell_words.json")
    resume_en = "I leverage cutting-edge tools to deliver seamless solutions."
    hits = scan_ai_tell(resume_en, ai_tell)
    hit_words = {h["word"] for h in hits}
    assert "leverage" in hit_words
    assert "cutting-edge" in hit_words
    assert "seamless" in hit_words

    resume_zh = "致力於賦能團隊，打造全方位解決方案。"
    hits_zh = scan_ai_tell(resume_zh, ai_tell)
    hit_words_zh = {h["word"] for h in hits_zh}
    assert "賦能" in hit_words_zh
    assert "打造" in hit_words_zh


def test_coverage_calc_no_false_positive_on_clean_resume():
    ai_tell = load_json("ai_tell_words.json")
    clean_resume = "帶領 3 人團隊於 6 個月內將轉換率從 2% 提升至 5%，使用 SQL 分析使用者行為。"
    hits = scan_ai_tell(clean_resume, ai_tell)
    assert hits == [], f"乾淨履歷不應命中 AI 味清單，但命中了: {hits}"


def run_all():
    tests = [
        test_contains_term_word_boundary,
        test_bilingual_synonym_match,
        test_missing_keyword_detected,
        test_ai_tell_detection,
        test_coverage_calc_no_false_positive_on_clean_resume,
    ]
    for t in tests:
        t()
        print(f"  ok: {t.__name__}")
    print("all tests passed")


if __name__ == "__main__":
    run_all()
