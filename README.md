# resume-jd-checker

繁體中文履歷 x JD 關鍵字健檢 Claude Skill。

市面上的 ATS 履歷檢查工具幾乎都是英文比對邏輯，遇到「JD 寫 Machine Learning、履歷寫機器學習」這種中英夾雜就失效。這個 Skill 專門處理這個比對盲點，並套用一套從 190+ 篇跨產業來源（Google/Goldman Sachs/McKinsey 官方招募指南、《The Google Resume》《What Color Is Your Parachute?》等權威著作、16 個職業別關鍵字庫）交叉整理出來的固定規則，給出具體、可解釋的建議，而不是空泛的「寫得不錯」。

## 功能
- **中英雙語關鍵字比對**：JD 用英文寫的技能、履歷用中文寫，一樣比對得到（目前科技/AI 產業深度支援，其他職業陸續擴充）
- **AI 用語偵測**：抓出履歷裡「聽起來太像 AI 生成」的空話（GPTism / 繁中 AI 味用詞），建議改寫成具體敘述
- **固定決策規則**：照片政策（依外商/台商/精簡版）、頁數（預設一頁）、格式（技能摘要前置的 hybrid 格式）、自傳（預設拿掉）、包裝程度（可驗證性檢查）
- **16 個職業別關鍵字庫**：業務、軟體工程師、PM、行銷、人資、電商、客服、金融顧問、教育、房仲、空服員、法律、餐飲、接案、醫護、設計

## 安裝
把這個資料夾放進 Claude Code 或 Claude Desktop 的 skills 目錄即可，或用 skills.sh：
```
npx skills add <github-username>/resume-jd-checker
```
（發布到 GitHub 後這個指令才會生效）

## 自我檢查
```
python3 scripts/test_keyword_match.py
```
純 Python 標準庫，不需要額外安裝套件。

## 手動測試比對邏輯
```
python3 scripts/keyword_match.py --resume <履歷txt路徑> --jd <JD txt路徑> --profession software_engineer
```
`--profession` 可選值見 `reference/profession_keywords.json` 的 key。

## 已知限制
- 雙語同義詞庫目前只深度做了科技/AI 產業（`reference/synonyms_tech.json`），其餘職業只有英文關鍵字池
- 職業分類是 Claude 讀 JD 後的主觀判斷，不是規則式分類器
- 決策規則（照片/頁數/格式/自傳）是特定使用者的個人決策彙整，不是放諸四海皆準的標準，使用前可依自己情境調整 `reference/decision_rules.md`

## 資料來源
完整彙整依據見 [reference/full-research-rubric.md](reference/full-research-rubric.md) 研究文件（190+ 篇來源，含 Gayle Laakmann McDowell《The Google Resume》、Richard N. Bolles《What Color Is Your Parachute?》等具名權威著作）。
