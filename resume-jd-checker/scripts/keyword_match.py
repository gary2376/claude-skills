#!/usr/bin/env python3
"""履歷 x JD 關鍵字健檢 —— 決定性比對邏輯（stdlib only，無外部依賴）。

用法：
    python3 keyword_match.py --resume resume.txt --jd jd.txt --profession software_engineer

輸出：JSON 到 stdout，欄位：
    matched          JD 有、履歷也有的關鍵字
    missing          JD 有、履歷沒有的關鍵字（優先修改對象）
    jd_coverage_pct  matched / (matched+missing) 的百分比
    ai_tell_hits     履歷中命中「AI 味」清單的詞，附上下文片段

設計取捨：不用 jieba 斷詞、不用 TF-IDF 抽取關鍵字。中文比對用子字串
包含判斷即可（不需要詞邊界）；候選關鍵字全部來自人工彙整的
profession_keywords.json，不做開放式關鍵字探勘 —— 這樣比對邏輯是
決定性、可解釋的，不依賴額外套件，安裝門檻低。
"""
import argparse
import json
import re
from pathlib import Path

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"


def load_json(name):
    with open(REFERENCE_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def contains_term(text, term):
    """大小寫不敏感的包含判斷。短英數詞（<=3字元）加詞邊界避免誤判
    （例如 "AI" 不該命中 "email" 裡的 "ai"）；中文/長詞直接子字串比對。"""
    text_l = text.lower()
    term_l = term.lower()
    if re.fullmatch(r"[a-z0-9/.+#-]+", term_l) and len(term_l) <= 3:
        return re.search(r"\b" + re.escape(term_l) + r"\b", text_l) is not None
    return term_l in text_l


def build_synonym_lookup(synonyms):
    """synonyms.json: canonical -> [aliases]。回傳 {canonical: [canonical]+aliases}。"""
    return {canon: [canon] + aliases for canon, aliases in synonyms.items()}


def expand_terms(keyword, synonym_lookup):
    """幫一個關鍵字找出所有應該一起比對的別名（含自己）。
    synonym_lookup 的 key 是小寫 canonical 詞，比對時雙向嘗試。"""
    kw_l = keyword.lower()
    if kw_l in synonym_lookup:
        return synonym_lookup[kw_l]
    for canon, aliases in synonym_lookup.items():
        if kw_l in [a.lower() for a in aliases]:
            return aliases
    return [keyword]


def match_keywords(resume_text, jd_text, keyword_pool, synonym_lookup):
    matched, missing = [], []
    for kw in keyword_pool:
        terms = expand_terms(kw, synonym_lookup)
        in_jd = any(contains_term(jd_text, t) for t in terms)
        if not in_jd:
            continue
        in_resume = any(contains_term(resume_text, t) for t in terms)
        (matched if in_resume else missing).append(kw)
    return matched, missing


def scan_ai_tell(resume_text, ai_tell):
    hits = []
    pools = [
        ("english", ai_tell["english"]["verbs"]),
        ("english", ai_tell["english"]["adjectives"]),
        ("english", ai_tell["english"]["transitions"]),
        ("english", ai_tell["english"]["hype"]),
        ("chinese", ai_tell["chinese"]["empty_words"]),
    ]
    for lang, words in pools:
        for w in words:
            idx = resume_text.lower().find(w.lower())
            if idx == -1:
                continue
            start, end = max(0, idx - 10), min(len(resume_text), idx + len(w) + 10)
            hits.append({"word": w, "lang": lang, "context": resume_text[start:end]})
    return hits


def main():
    ap = argparse.ArgumentParser(description="履歷 x JD 關鍵字健檢")
    ap.add_argument("--resume", required=True, help="履歷文字檔路徑")
    ap.add_argument("--jd", required=True, help="JD 文字檔路徑")
    ap.add_argument("--profession", required=True, help="profession_keywords.json 裡的 key")
    ap.add_argument("--synonyms", default=None, help="額外雙語同義詞庫檔名（在 reference/ 底下），預設 synonyms_tech.json")
    args = ap.parse_args()

    resume_text = Path(args.resume).read_text(encoding="utf-8")
    jd_text = Path(args.jd).read_text(encoding="utf-8")

    professions = load_json("profession_keywords.json")
    if args.profession not in professions:
        raise SystemExit(
            f"未知職業 key: {args.profession}，可用選項: {', '.join(professions)}"
        )
    keyword_pool = professions[args.profession]["keywords"]

    synonyms_file = args.synonyms or "synonyms_tech.json"
    synonyms_path = REFERENCE_DIR / synonyms_file
    synonyms = {}
    if synonyms_path.exists():
        raw = load_json(synonyms_file)
        synonyms = {k: v for k, v in raw.items() if not k.startswith("_")}
    synonym_lookup = build_synonym_lookup(synonyms)

    matched, missing = match_keywords(resume_text, jd_text, keyword_pool, synonym_lookup)
    total = len(matched) + len(missing)
    coverage = round(100 * len(matched) / total, 1) if total else None

    ai_tell = load_json("ai_tell_words.json")
    ai_tell_hits = scan_ai_tell(resume_text, ai_tell)

    result = {
        "profession": professions[args.profession]["label"],
        "matched": matched,
        "missing": missing,
        "jd_coverage_pct": coverage,
        "ai_tell_hits": ai_tell_hits,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
