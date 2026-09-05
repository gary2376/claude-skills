# bigtech-career-radar

追蹤台灣/全球大公司AI/ML/軟體職缺訊號，轉成有優先順序的學習路線圖 Claude Skill。核心差異化：把來源可信度當一等公民——官方API/官方頁 vs 104人工入口 vs 被擋的頁面分開處理，被擋就老實寫被擋，不會把搜尋引擎雜訊腦補成技能趨勢。

## 安裝

在終端機執行（或直接貼給你的 agent 執行）：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/bigtech-career-radar
```
會自動偵測目前的 agent（Claude Code、Codex、Cursor 等）裝到對應路徑，不限 Claude 專用。

## 功能

- 兩階段管線：收集（只用官方/第一方來源，含API如MediaTek tRPC/Workday/AUO、RSS、以及可解析的官方careers頁如Google/Acer SuccessFactors）+ 分析（轉成P1/P2/P3學習優先順序）
- 三層來源分級（可直接信任／官方入口證據不足／僅供人工複查），拒絕把104雜訊或被擋頁面當成有效證據
- 跨公司職缺家族分群方法，避免逐字比對職缺標題漏掉真實重疊
- 三種輸出格式（完整分析／週報壓縮／職缺家族雷達），依情境挑

## 使用

裝好後直接問「幫我看台積電/聯發科/Google最近在找什麼AI職缺」或「這些大公司職缺該學什麼技能」，也可以要求「幫我設定每週追蹤」。

## 範例

**輸入**：「幫我追蹤大公司AI職缺，順便告訴我該學什麼」

**輸出（節錄）**
> ## 可直接信任的官方訊號
> - 聯發科：機器學習算法工程師(約聘)｜新竹｜官方tRPC API
> - Google：Senior Software Engineer, Cloud AI/ML Infrastructure｜台灣｜官方職缺頁
> - 台積電：官方職缺頁403，本週無足夠有效訊號
>
> ## 學習優先順序
> - P1：Python backend、API、RAG、vector DB（跨聯發科/Google重複出現）
> - P2：agent tool-calling、workflow設計（Google/趨勢科技出現，樣本中等）

## 已知限制

見`SKILL.md`「已知限制」一節——預設公司池是台灣大公司、官方存取方式會隨網站改版而失效、104板長期沒有穩定機器可解析路徑。
