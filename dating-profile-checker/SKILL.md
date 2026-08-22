---
name: dating-profile-checker
description: "Use when the user wants feedback on a dating app profile/bio (交友軟體自我介紹、約會檔案、Tinder/Bumble/Hinge 自介), asks whether their profile is too generic or boring, or wants help improving match rate. Diagnoses the bio against a fixed rubric built from Hinge's internal engagement data, Bumble's 2025 Global Dating Trends report, SwipeStats.io's independent third-party analysis of 7,079 real profiles, and 2023-2025 peer-reviewed self-presentation research — explicitly flags that Hinge/Bumble (specific & detailed wins) and SwipeStats' independent Tinder data (short & mysterious wins for men) point in opposite directions depending on platform and dating goal (fast matching vs serious relationship), and applies whichever rule fits. By default only diagnoses (classifies content into empty filler / vague-but-real interests / bare identity tag) and asks clarifying questions — never fabricates specific details the user didn't provide, and only writes a full rewrite after the user supplies more material and explicitly asks for a polish."
---

# 交友檔案健檢

繁體中文交友軟體自介分析 Skill。核心差異化：市面上的自介優化工具幾乎都預設「具體、真實、寫多一點」是唯一正解，這個 Skill 處理的是一個大部分工具沒處理的落差——Hinge、Bumble 自己的數據都主張具體詳細比較好，但獨立第三方分析真實 Tinder 數據卻發現相反結果（男性簡短、留神秘感配對率反而更高）。這代表「怎麼寫」沒有單一答案，取決於使用者在哪個平台、想要什麼。這個 Skill 先問清楚平台跟目標，再套用對應的規則，而不是給一套放諸四海皆準的建議。

## 何時觸發

使用者貼交友軟體自介文字想請人看看，或問「這個自介好不好」「為什麼配對率很低」「幫我看看我的 Tinder/Bumble/Hinge 檔案」。

## 執行流程

1. **取得自介文字**：使用者貼文字，直接用。

2. **問清楚平台 + 目標**（核心步驟，對應第一段講的資料矛盾）：
   - 平台：Tinder / Bumble / Hinge / 其他
   - 目標：快速多配對 / 認真找對象
   - 目前環境若有原生互動式提問工具（例如 Claude Code 的 AskUserQuestion），優先用它一次問完這兩件事；沒有的話用文字一次問完，不要分兩輪。
   - 使用者沒講平台或目標就想先看意見，可以先給初步觀察，但**套用 `decision_rules.md` 第 2 節的長度/策略建議前一定要先問清楚**，不要用其中一種平台的邏輯去套用在使用者沒說清楚的情境。

3. **跑決定性檢查腳本**：
   ```
   python3 scripts/profile_check.py --bio <bio.txt> --platform <platform> --goal <goal>
   ```
   輸出 JSON：`char_count`、`empty_adjective_hits`（空話形容詞命中）、`generic_interest_hits`（籠統但真實的興趣清單命中）、`identity_only`（是否為純身份標籤型自介）、`length_recommendation`（依平台+目標查表的長度建議）。

4. **套用 `reference/decision_rules.md` 第 1 節的三類分類邏輯，分開處理，不要用同一套規則**：
   - `empty_adjective_hits`：建議精簡或刪除
   - `generic_interest_hits`：**不建議刪除**，提示使用者「有沒有想到其中一項的具體例子」，有的話才升級，沒有就保留原樣
   - `identity_only` 為 true：不能硬掰內容，反問使用者「有沒有一件最近在做/在意/覺得好笑的小事」，並提醒身份資料通常已顯示在平台結構化欄位

5. **輸出繁體中文診斷報告**（預設只做到這裡，不要主動代寫完整改寫版本）：
   - 空話形容詞清單（建議精簡/刪除，附理由）
   - 籠統但真實的興趣清單（保留，附一句反問看使用者有沒有具體例子）
   - 已有的具體素材（如果有，指出來，並問使用者能不能再補一層細節）
   - 長度建議（附平台+目標依據）
   - 結尾問使用者要不要補充素材、要不要進到潤飾階段

6. **只有使用者針對建議補充了新素材，並明確要求審核/潤飾，才進到改寫階段**：
   - 改寫只能用使用者剛剛補充的內容組合，**不能加入使用者沒提過的情節、地點、心情、細節**
   - 給出改寫版本後，附一句「為什麼這樣改」，query `reference/decision_rules.md` 第 4 節引用依據表，格式「這是 [問題] —— 依據 [來源]：[主張]」，一句話帶過，不要整段複製來源介紹

## 檔案結構
```
SKILL.md
reference/
  cliche_phrases.json   空話形容詞 + 籠統興趣清單詞庫，兩類分開處理
  decision_rules.md     三類分類邏輯 + 平台×目標長度建議表 + 引用依據表 + 不捏造規則
  research.md           四層證據彙整（學術研究/平台官方數據/獨立第三方數據/台灣本地證據）
scripts/
  profile_check.py      決定性比對邏輯（stdlib only，無外部依賴）
  test_profile_check.py 自我檢查（python3 scripts/test_profile_check.py）
```

## 已知限制（誠實列出，不要對使用者過度承諾）
- 只處理自介文字，不處理照片——照片挑選、排序這塊研究也有(例如 Hinge 數據顯示活動照比靜態擺拍留言多 3 倍)，但目前沒有建置成規則，使用者問照片建議時要老實說明這塊還沒做
- 台灣目前查不到任何一位具名心理師或近期正式學術研究是專門針對「交友軟體自介寫作」發表看法的，中文範本語感只能參考台灣媒體文章跟社群觀察，不能包裝成專家背書，見 `decision_rules.md` 第 5 節
- `identity_only` 判斷是字數門檻 + 關鍵字命中的啟發式，不是語意理解，字數卡在門檻邊緣或用詞沒中關鍵字池時可能誤判，抓不準時用常識判斷
- `generic_interest_categories` 詞庫目前只涵蓋常見類別，冷門興趣不會被抓到，這時候直接當成「已有的具體素材」處理即可，不用勉強套進籠統清單
- OkCupid OkTrends 的研究對象是「開場白/第一則訊息」，不是自介本身，跟使用者說明這條依據時要注意範疇差異，不要混講成自介研究
