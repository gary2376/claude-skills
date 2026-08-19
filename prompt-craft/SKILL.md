---
name: prompt-craft
description: "Use when the user has a vague/underspecified request they want to turn into a well-formed prompt for an AI tool (any AI, not just Claude) — e.g. \"幫我寫封信\" \"幫我看一下這份資料\" \"幫我回這個客訴\" without saying who it's for, what format, or what tone. Also use when the user explicitly asks how to write a better prompt, or says a prompt/reply from an AI came out wrong because they didn't specify enough. Detects which of 6 dimensions (role/context/format/audience-tone/example/constraints) are missing from the raw request, asks ONE consolidated clarifying question for what's missing (does not silently guess), then assembles a structured prompt with a one-line note explaining why each filled-in field matters — grounded in Anthropic/OpenAI/Google's own prompt engineering guides plus workplace-survey data on why non-technical staff struggle to prompt (34% confident at task decomposition, LinkedIn/TalentLMS 2026)."
---

# prompt-craft — 模糊需求轉可用 Prompt

繁體中文職場向 Prompt 助手 Skill。核心差異化：市面上 SurePrompts、GetEasyPrompt 等工具都是「使用者填好一段話 →
吐出結構化 prompt」的單向黑箱轉換，這個 Skill 不做這件事的重製——它處理的是「使用者連自己漏講了什麼都不知道」
這個更前面的問題：偵測缺漏欄位、主動反問、解釋為什麼要補，而不是預設使用者已經知道答案只是懶得填。

## 何時觸發

使用者丟一句模糊的任務描述想請 AI 幫忙（例如「幫我寫封信跟主管請假」「幫我看一下這份業績資料」「幫我回這則客訴」），
或直接問「我這個 prompt 要怎麼寫比較好」「AI 幫我寫的東西不是我要的，是不是我沒講清楚」。

## 執行流程

1. **取得原始需求文字**，寫成暫存檔（例如 `/tmp/prompt_request_<random>.txt`）供腳本使用。

2. **跑決定性缺漏偵測腳本**
   ```
   python3 scripts/gap_check.py --request <request.txt>
   ```
   輸出 JSON：`char_count`、`wish_type`（是否判定為一句話願望型指令）、`detected`（命中的維度）、
   `missing`（沒命中、值得反問的維度）。

3. **判斷要不要走「願望型」快速路徑**
   - `wish_type` 為 true：不要逐一念 6 個維度，先照 `reference/decision_rules.md` 的 wish_type 話術，
     問一句「這個任務具體想達成什麼結果？」，拿到具體任務後再重新評估還缺哪些維度。
   - `wish_type` 為 false 但 `missing` 非空：判斷這個需求屬於 `decision_rules.md`「4 個優先場景」
     的哪一種，只問該場景優先序裡的維度，不要 6 個全問——問太多使用者會放棄。

4. **一次問完，不要一問一答式來回**。把要問的問題整理成一段話（1-3 個問題），不要每個維度開一輪對話。
   使用者說「不用問了，直接猜」或給的資訊已經足夠合理猜測時，可以跳過反問，但要在最終輸出裡註明
   「這幾點是我猜的，不對的話跟我說」。
   - **目前環境若有原生互動式提問工具（例如 Claude Code 的 AskUserQuestion），優先用它問**：把
     `missing` 裡最重要的 1-2 個維度組成選項（選項用該場景常見答案當預設，加一個自由輸入項），
     不要每個維度分開開一輪。沒有這類工具的環境（Claude Desktop、網頁版）就退回純文字一次問完，
     行為邏輯不變，只是呈現方式不同——不要因為沒有選單工具就跳過反問。

5. **組出最終 prompt**，用這 6 個維度組織（不用綁死 CO-STAR/RTF 等單一框架名稱，這些框架本質上是同一組
   維度的不同排列，見 `reference/research.md` 第一節）：角色／身分、背景／脈絡、任務目標、輸出格式、
   受眾／語氣、範例／限制。

6. **每個由使用者回答或由你合理補上的欄位，附一句「為什麼要補這個」**，查 `reference/decision_rules.md`
   的引用依據欄位，格式「這是 [具體問題] —— 依據 [人物/機構/框架]：[核心主張]」，一句話帶過，不要整段
   複製來源介紹。找不到對應的不要硬套引用湊數。

7. **輸出結構建議**：
   - 組好的結構化 prompt（使用者可以直接複製去用的版本）
   - 1-3 句「為什麼這樣補」的教學說明（帶引用）
   - 若原始需求判定是 wish_type 或 missing 欄位很多，簡短提醒使用者這類需求下次可以先想清楚哪些點
     （呼應 34% 員工對 task decomposition 沒信心這個數據，順手做一點教育，不用說教）

## 檔案結構
```
SKILL.md
reference/
  gap_keywords.json    6 個維度的雙語關鍵字池
  decision_rules.md    反問話術 + 引用依據表 + 4 個優先場景
  research.md          跨 7 類來源的研究彙整（框架比較、常見錯誤、實證數據、競品掃描）
scripts/
  gap_check.py          決定性缺漏偵測（stdlib only，無外部依賴）
  test_gap_check.py      自我檢查（python3 scripts/test_gap_check.py）
```

## 已知限制（誠實列出，不要對使用者過度承諾）
- 6 維度偵測是關鍵字子字串命中，不是語意理解，可能誤判「使用者其實有講但用詞沒中關鍵字池」——抓不準時
  用常識判斷，不要盲信腳本輸出，見 `reference/decision_rules.md` 結尾的限制說明。
- 目前只深度在地化「職場書信/會議紀錄/資料分析/客服回覆」4 個場景，其他情境（例如創意寫作、程式碼生成）
  的優先序沒有特化，會退回問全部 6 個維度。
- `wish_type` 判斷用字數門檻（20字），是經驗值不是精算，長句廢話可能被誤判成「講清楚了」。
