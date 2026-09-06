# bigtech-career-radar

追蹤任何產業/公司的官方職缺訊號，轉成有優先順序的學習路線圖 Claude Skill。核心差異化：把來源可信度當一等公民——官方API/官方頁 vs 人工入口 vs 被擋的頁面分開處理，被擋就老實寫被擋，不會把搜尋引擎雜訊腦補成技能趨勢。**不限AI/科技業**——公司清單跟關鍵字都在`config.json`裡，內建AI/台灣大公司、台灣臨床心理師、台灣壽險業三份範例，都真的跑過驗證有抓到真實職缺。

## 安裝

在終端機執行（或直接貼給你的 agent 執行）：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/bigtech-career-radar
```
會自動偵測目前的 agent（Claude Code、Codex、Cursor 等）裝到對應路徑，不限 Claude 專用。

## 功能

- config驅動：換產業/公司池只要改JSON，不用碰程式碼
- 7種解析器：3種通用型（Workday平台、WordPress公會徵才頁、中文欄位標籤頁）+ 4種公司專屬範例（MediaTek tRPC、Acer SuccessFactors、AUO、Google）
- 三層來源分級（可直接信任／官方入口證據不足／僅供人工複查），拒絕把job board雜訊或被擋頁面當成有效證據
- 兩階段管線：收集（只用官方/第一方來源）+ 分析（轉成P1/P2/P3學習優先順序）

## 使用

裝好後直接問「幫我看台積電/聯發科/Google最近在找什麼AI職缺」，或換產業問「幫我追蹤心理師/保險業職缺，該學什麼技能」——沒有現成設定檔的話，agent會照SKILL.md的步驟幫你判斷目標公司/機構能不能自動解析，建一份新的`config.<產業>.json`。

## 範例

**輸入**：「幫我追蹤台灣臨床心理師職缺，該學什麼技能」

**輸出（節錄，`config.psychologist-tw.json`真實跑出來的）**
> ## 台灣臨床心理學會官方職缺（wordpress_category）
> - [1] 花蓮慈濟醫院癌症醫學中心 徵求臨床心理師
>   資格條件：1.碩士以上心理相關科系畢業，具心理師證書及執照，以臨床心理師優先考慮。2.完成PGY訓練者佳。3.曾有癌症或末期病人心理腫瘤服務經驗者佳。
>
> ## 本次可關注方向
> - 兒童 / 早期療育臨床心理
> - 精神醫療 / 危機處遇
> - 腫瘤 / 安寧心理照護

## 我自己怎麼用

先跑這個skill找出目標領域市場真的在要什麼技能 → 針對缺口去找對應教學影片，用[youtube-content](../youtube-content/)這個skill轉成逐字稿摘要 → 把兩邊輸出餵進LLM Wiki持續累積。

**實例**：跑一次AI／台灣大公司設定，抓到「Cloud platform / release engineering」跟「MLOps」是市場熱門但我作品集缺的方向——這就是我下一步要補的技能。

## 已知限制

見`SKILL.md`「已知限制」一節——`labeled_html_page`解析器的中文欄位別名是從2個真實案例歸納的，換網站可能要擴充別名；遇到CAPTCHA/企業級WAF/純JS渲染的頁面(104、1111人力銀行等)一律標人工複查，不嘗試繞過反爬蟲機制。
