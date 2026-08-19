#!/usr/bin/env python3
"""prompt-craft —— 缺漏欄位偵測（stdlib only，無外部依賴）。

用法：
    python3 gap_check.py --request request.txt

輸出：JSON 到 stdout，欄位：
    char_count       去除空白後的字數
    wish_type        是否判定為「一句話願望型指令」（過短 + 缺漏維度過多）
    detected         命中關鍵字的維度清單
    missing          沒命中關鍵字的維度清單（照 gap_keywords.json 順序，每個附 label）

設計取捨：跟 resume-jd-checker/scripts/keyword_match.py 同一套決定性子字串
比對哲學——不做斷詞、不用 NLP 模型判斷「使用者是不是真的講了角色/格式」，
只做關鍵字命中的保守判斷。命中不代表寫得好，沒命中也不代表一定要補，
只是先給 Claude 一份「值得反問使用者」的候選清單，最終判斷跟提問方式
交給 Claude 對照 reference/decision_rules.md 決定。
"""
import argparse
import json
import re
from pathlib import Path

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"
WISH_TYPE_CHAR_THRESHOLD = 20  # 願望型指令的字數門檻（含空白前），來自 research.md 第二節「單一句話願望型指令」


def load_json(name):
    with open(REFERENCE_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def contains_term(text, term):
    """大小寫不敏感的包含判斷。短英數詞（<=3字元）加詞邊界避免誤判。"""
    text_l = text.lower()
    term_l = term.lower()
    if re.fullmatch(r"[a-z0-9/.+#-]+", term_l) and len(term_l) <= 3:
        return re.search(r"\b" + re.escape(term_l) + r"\b", text_l) is not None
    return term_l in text_l


def detect_dimensions(text, gap_keywords):
    detected, missing = [], []
    for key, info in gap_keywords.items():
        if key == "_note":
            continue
        hit = any(contains_term(text, kw) for kw in info["keywords"])
        (detected if hit else missing).append({"key": key, "label": info["label"]})
    return detected, missing


def main():
    ap = argparse.ArgumentParser(description="prompt-craft 缺漏欄位偵測")
    ap.add_argument("--request", required=True, help="使用者原始需求描述的文字檔路徑")
    args = ap.parse_args()

    text = Path(args.request).read_text(encoding="utf-8").strip()
    gap_keywords = load_json("gap_keywords.json")

    detected, missing = detect_dimensions(text, gap_keywords)
    char_count = len(re.sub(r"\s+", "", text))
    wish_type = char_count < WISH_TYPE_CHAR_THRESHOLD and len(missing) >= 4

    result = {
        "char_count": char_count,
        "wish_type": wish_type,
        "detected": detected,
        "missing": missing,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
