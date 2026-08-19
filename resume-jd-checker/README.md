# resume-jd-checker

繁體中文履歷 x JD 關鍵字健檢 Claude Skill。

市面上的 ATS 履歷檢查工具幾乎都是英文比對邏輯，遇到「JD 寫 Machine Learning、履歷寫機器學習」這種中英夾雜就失效。這個 Skill 專門處理這個比對盲點，並套用一套從 190+ 篇跨產業來源（Google/Goldman Sachs/McKinsey 官方招募指南、《The Google Resume》《What Color Is Your Parachute?》等權威著作、16 個職業別關鍵字庫）交叉整理出來的固定規則，給出具體、可解釋的建議，而不是空泛的「寫得不錯」。

## 安裝（推薦：直接叫 Claude 幫你裝）

不用自己下載檔案、不用改路徑。打開 Claude Code 或 Claude Desktop，貼上這段話：

```
幫我安裝這個 Claude Skill：https://github.com/gary2376/claude-skills/tree/master/resume-jd-checker
複製到 ~/.claude/skills/resume-jd-checker
```

Claude 會自己 clone、複製、確認檔案到位，裝完直接可以用。

<details>
<summary>其他安裝方式（手動）</summary>

用 [skills CLI](https://github.com/vercel-labs/skills)：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/resume-jd-checker
```
（monorepo 子資料夾要用完整 GitHub tree URL，不能只寫 `owner/repo/子資料夾`）

或手動複製資料夾：把 `resume-jd-checker/` 整個資料夾複製進 `~/.claude/skills/`（全域）或專案裡的 `.claude/skills/`（僅該專案可用）。
</details>

## 怎麼用

裝好之後，直接在 Claude 對話裡貼你的履歷（文字或 PDF 路徑）+ 想投的 JD（文字或連結），或問「幫我看這份履歷符不符合這個 JD」「這句話是不是太 AI 了」，Claude 會自動觸發這個 Skill，不用自己跑任何指令。

## 功能
- **中英雙語關鍵字比對**：JD 用英文寫的技能、履歷用中文寫，一樣比對得到（目前科技/AI 產業深度支援，其他職業陸續擴充）
- **AI 用語偵測**：抓出履歷裡「聽起來太像 AI 生成」的空話（GPTism / 繁中 AI 味用詞），建議改寫成具體敘述
- **固定決策規則**：照片政策（依外商/台商/精簡版）、頁數（預設一頁）、格式（技能摘要前置的 hybrid 格式）、自傳（預設拿掉）、包裝程度（可驗證性檢查）
- **建議附權威來源**：命中常見錯誤時附上具名依據（Gayle Laakmann McDowell、Richard N. Bolles、Google 官方招募建議等），不是憑空給意見
- **16 個職業別關鍵字庫**：業務、軟體工程師、PM、行銷、人資、電商、客服、金融顧問、教育、房仲、空服員、法律、餐飲、接案、醫護、設計

## 已知限制
- 雙語同義詞庫目前只深度做了科技/AI 產業（`reference/synonyms_tech.json`），其餘職業只有英文關鍵字池
- 職業分類是 Claude 讀 JD 後的主觀判斷，不是規則式分類器，遇到清單外的職業（例如「汽車修理工」）會誠實告知沒有對應關鍵字庫
- 決策規則（照片/頁數/格式/自傳）是特定使用者的個人決策彙整，不是放諸四海皆準的標準，使用前可依自己情境調整 `reference/decision_rules.md`

## 資料來源
完整彙整依據見 [reference/full-research-rubric.md](reference/full-research-rubric.md) 研究文件（190+ 篇來源，含 Gayle Laakmann McDowell《The Google Resume》、Richard N. Bolles《What Color Is Your Parachute?》等具名權威著作）。

---

## 給開發者 / 貢獻者

比對邏輯是決定性 Python 腳本（stdlib only，無外部依賴），不是每次都靠 Claude 現場判斷，方便驗證正確性。

自我檢查（跑內建的 5 條 assert 測試）：
```
python3 scripts/test_keyword_match.py
```

手動測試比對邏輯：
```
python3 scripts/keyword_match.py --resume <履歷txt路徑> --jd <JD txt路徑> --profession software_engineer
```
`--profession` 可選值見 `reference/profession_keywords.json` 的 key。
