#!/usr/bin/env python3
"""dating-profile-checker —— 交友檔案自介決定性檢查（stdlib only，無外部依賴）。

用法：
    python3 profile_check.py --bio bio.txt --platform tinder --goal fast

輸出：JSON 到 stdout，欄位：
    char_count              去除空白後的字數
    empty_adjective_hits    命中「空話形容詞」的詞（建議精簡/刪除）
    generic_interest_hits   命中「籠統但真實的興趣清單」的詞（建議保留，提示可升級）
    identity_only           是否判定為「純身份標籤型」自介（沒有其他內容可用，要反問）
    length_recommendation   依 platform+goal 查表得到的長度建議區間與依據

設計取捨：跟 resume-jd-checker/scripts/keyword_match.py、prompt-craft/scripts/gap_check.py
同一套決定性子字串比對哲學——不做斷詞、不用 NLP 模型判斷語意，只做保守的關鍵字命中判斷。
命中空話形容詞不代表這句話一定要刪，是否刪除、怎麼跟使用者說明，交給 Claude 對照
reference/decision_rules.md 決定，這支腳本只負責產生決定性的候選清單。
"""
import argparse
import json
import re
from pathlib import Path

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"

# 純身份標籤型判斷的字數門檻，來自 decision_rules.md 第 1 節：
# 字數極短 + 只含年齡/身份格式 + 沒有命中其他兩類詞，才判定為「沒有內容可用」
IDENTITY_ONLY_CHAR_THRESHOLD = 15

# 平台 × 目標 長度建議表，數字與依據見 reference/decision_rules.md 第 2 節
LENGTH_TABLE = {
    ("tinder", "fast"): {
        "range": "15-45 字",
        "note": "Tinder 官方建議區間；SwipeStats 獨立數據：男性 1-50 字元配對率比 151-300 字元高 73%",
    },
    ("tinder", "serious"): {
        "range": "45-100 字",
        "note": "比純快速配對略長，但至少留一個具體可追問的細節，不要完全省略",
    },
    ("hinge", "fast"): {
        "range": "三個 prompt 欄位都填",
        "note": "Hinge 內部數據：填滿三欄位配對品質高 73%",
    },
    ("hinge", "serious"): {
        "range": "三個 prompt 欄位都填，內容更具體",
        "note": "Hinge 內部數據：具體細節表現贏過修飾過的句子",
    },
    ("bumble", "fast"): {
        "range": "50-150 字",
        "note": "Bumble《2025 Global Dating Trends》：避免模板化，中等長度",
    },
    ("bumble", "serious"): {
        "range": "80-200 字",
        "note": "Bumble《2025 Global Dating Trends》：真實具體、個人深度優先",
    },
}


def load_json(name):
    with open(REFERENCE_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def contains_term(text, term):
    return term in text


def detect_hits(text, phrase_list):
    return [p for p in phrase_list if contains_term(text, p)]


def detect_identity_only(text, char_count, cliche_data, empty_hits, interest_hits):
    if char_count > IDENTITY_ONLY_CHAR_THRESHOLD:
        return False
    if empty_hits or interest_hits:
        return False
    occupation_terms = cliche_data["identity_only_hints"]["occupation_or_status"]
    has_occupation = any(contains_term(text, t) for t in occupation_terms)
    has_age = re.search(r"\d{1,2}\s*(y|Y|歲)", text) is not None
    return has_occupation or has_age


def main():
    ap = argparse.ArgumentParser(description="dating-profile-checker 自介決定性檢查")
    ap.add_argument("--bio", required=True, help="使用者自介文字檔路徑")
    ap.add_argument("--platform", required=True, choices=["tinder", "bumble", "hinge", "other"])
    ap.add_argument("--goal", required=True, choices=["fast", "serious"])
    args = ap.parse_args()

    text = Path(args.bio).read_text(encoding="utf-8").strip()
    cliche_data = load_json("cliche_phrases.json")

    char_count = len(re.sub(r"\s+", "", text))
    empty_hits = detect_hits(text, cliche_data["empty_adjectives"])
    interest_hits = detect_hits(text, cliche_data["generic_interest_categories"])
    identity_only = detect_identity_only(text, char_count, cliche_data, empty_hits, interest_hits)

    if args.platform == "other":
        length_rec = {"range": "無查表資料", "note": "目前長度建議表只涵蓋 Tinder/Bumble/Hinge，其他平台請用常識判斷或請使用者補充平台特性"}
    else:
        length_rec = LENGTH_TABLE[(args.platform, args.goal)]

    result = {
        "char_count": char_count,
        "empty_adjective_hits": empty_hits,
        "generic_interest_hits": interest_hits,
        "identity_only": identity_only,
        "length_recommendation": length_rec,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
