---
name: resume-jd-checker
description: "Use when the user wants to check or improve a resume (履歷) against a job description (JD), asks for ATS keyword gap analysis, wants feedback on Traditional Chinese resume writing, or asks whether their resume 'sounds too AI-generated'. Compares a resume against a JD using a bilingual (中英) keyword dictionary, flags AI-cliché phrasing (GPTism / 中文AI味用詞), and applies a fixed rubric distilled from Google/Goldman Sachs/McKinsey official hiring guides plus 190+ cross-industry sources (photo policy by employer type, one-page default, skills-first hybrid format, no autobiography, moderate-embellishment check)."
---

# 履歷 x JD 關鍵字健檢

繁體中文履歷分析 Skill。核心差異化：市面 ATS 履歷工具幾乎都是英文比對，這個 Skill 處理「JD 寫 Machine Learning、履歷寫機器學習」這種中英夾雜的比對盲點，並套用一套已經被使用者拍板、來自 190+ 篇跨產業來源交叉驗證的固定規則，而不是空泛地說「寫得不錯/要加強」。

## 何時觸發
使用者提供履歷（貼文字、PDF、或檔案路徑）+ 想投遞的 JD（貼文字或連結），或單純問「我的履歷這樣寫可以嗎」「這句話是不是太 AI 了」。

## 執行流程

1. **取得履歷文字**
   - 使用者貼文字：直接用
   - 使用者給 PDF/docx 路徑：用 Read 工具直接讀取（Read 工具原生支援 PDF，不需要額外安裝 pdfplumber 等套件），把抽出的文字寫成暫存檔（例如 `/tmp/resume_<random>.txt`）供下一步腳本使用

2. **取得 JD 文字**
   - 使用者貼文字：直接用
   - 使用者給連結：用 WebFetch 抓取 JD 內容，同樣寫成暫存 txt

3. **判斷職業類別**
   - 讀 JD 內容，判斷最貼近 `reference/profession_keywords.json` 裡的哪一個 key（16 選項：sales、software_engineer、product_manager、marketing_social、hr、ecommerce、customer_service、finance_advisor、education_tutor、real_estate、flight_attendant、legal、food_service、freelancer、healthcare_nursing、design_creative）
   - 抓不準就選最接近的，並跟使用者說明你的判斷

4. **跑決定性比對腳本**
   ```
   python3 scripts/keyword_match.py --resume <resume.txt> --jd <jd.txt> --profession <key>
   ```
   - 若職業類別是 `software_engineer` 且判斷跟 AI/資料/後端相關，腳本預設會用 `reference/synonyms_tech.json` 做雙語比對（這是目前唯一深度建置的雙語同義詞庫，其餘職業類別目前只有英文關鍵字池，比對時仍會運作，只是沒有雙語擴充）
   - 腳本輸出 JSON：`matched`（已命中）、`missing`（JD 有履歷沒有，優先修改對象）、`jd_coverage_pct`、`ai_tell_hits`（命中 AI 味清單的詞與上下文）

5. **套用 `reference/decision_rules.md` 的 6 條固定規則**，檢查使用者履歷有沒有違反：照片政策（依外商/台商/精簡版判斷）、頁數（預設一頁）、格式（技能摘要前置＋時間序佐證的 hybrid 格式，不要純技能導向）、自傳（預設建議拿掉）、包裝程度（可驗證性檢查）
   - 這些規則**直接套用，不要跟使用者呈現成「有兩派意見」**——使用者已經拍板決策，見 `reference/decision_rules.md` 開頭說明

6. **輸出繁體中文報告**，結構建議：
   - 關鍵字缺口（missing 清單，按重要性排序，說明為什麼 JD 提到但履歷沒有很致命）
   - AI 用語警示（ai_tell_hits，逐條給出「原句 → 建議改寫方向」，不要直接幫使用者代寫整句，除非使用者要求）
   - 格式/決策規則檢查（哪些違反了固定規則，附 `decision_rules.md` 裡的依據）
   - 2-3 條最優先要修改的具體建議（不要落落長列一堆，挑最重要的先講）
   - **給建議時，查 `decision_rules.md` 第 7 節「引用依據」表，命中的話附上具體人物/機構＋核心主張（一句話帶過，不要整段複製介紹）；沒對應的常見錯誤（例如純粹的錯字/格式錯誤）不用硬掛引用湊數**
   - **對可能第一次用這個 Skill 的使用者，第一次出現「JD」這種縮寫時順手展開一次（JD＝Job Description，職缺說明/徵才內容），不要預設使用者懂求職圈術語**

## 檔案結構
```
SKILL.md
reference/
  profession_keywords.json   16 個職業的加分關鍵字池
  synonyms_tech.json         科技/AI 產業雙語同義詞庫（旗艦深度，其他職業待擴充）
  ai_tell_words.json         英文 GPTism + 繁中 AI 味用詞清單
  decision_rules.md          6 條固定決策規則 + 量化公式 + Experience 黃金結構
scripts/
  keyword_match.py           決定性比對邏輯（stdlib only，無外部依賴）
  test_keyword_match.py      自我檢查（python3 scripts/test_keyword_match.py）
```

## 已知限制（誠實列出，不要對使用者過度承諾）
- 雙語同義詞庫目前只深度建置了科技/AI 產業（`synonyms_tech.json`），其餘 15 個職業只有英文關鍵字池，比對得到「JD 有沒有出現在履歷」，但抓不到中英夾雜的同義詞
- 職業判斷是 Claude 讀 JD 後的主觀判斷，不是規則式分類器，邊界職業（例如「業務型 PM」）可能判斷不準，抓不準時要主動跟使用者確認
- `reference/decision_rules.md` 的規則是使用者個人決策，不是放諸四海皆準的鐵律（例如「一頁為主」在某些資深/學術情境不適用，規則裡有寫明例外）
