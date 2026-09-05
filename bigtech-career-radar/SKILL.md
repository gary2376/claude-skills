---
name: bigtech-career-radar
description: "Use when the user wants to monitor AI/ML/software hiring signals at major tech companies (Taiwan or global) and turn them into a learning-priority roadmap — e.g. '幫我看台積電/聯發科/Google最近在找什麼AI職缺', '追蹤大公司AI職缺趨勢', '這些職缺該學什麼技能', or wants a recurring weekly digest of this. Two-stage pipeline: a collector that pulls only official/first-party sources (with per-company retrieval recipes: MediaTek tRPC API, TSMC 403 handling, Workday-based companies, AUO/Google job APIs) tiered by trust, and an analyzer that turns the collected evidence into P1/P2/P3 learning priorities. Core differentiator: refuses to launder blocked pages, search-engine snippets, or 104-board noise into confident hiring-trend claims — every conclusion is tagged with its evidence tier."
---

# 大公司AI職涯訊號雷達

追蹤台灣/全球大公司的AI/ML/軟體職缺訊號，轉成有優先順序的學習路線圖。核心差異化：市面上多數「職缺爬蟲/技能雷達」是把搜尋引擎結果或104關鍵字命中直接當成市場需求，這個skill把「來源可信度」當一等公民——官方API/官方頁 vs 104人工入口 vs 被擋的頁面，分開處理，被擋就老實寫被擋，不腦補技能方向。

這套三層來源分級跟兩階段管線設計，是從實際反覆執行、觀察各公司來源穩不穩定之後整理出來的規則，不是憑空設計的規則。

## 何時觸發

使用者問：
- 現在大公司AI/軟體職缺在找什麼技術？
- 我該學什麼才能進台積電/聯發科/Google/NVIDIA這類公司？
- 幫我定期追蹤職缺市場，看技能需求有沒有變化
- 把一堆職缺整理成實際的學習路線
- 想擴大追蹤的公司池，判斷哪些公司值得監控
- 想知道哪些職缺家族在多家公司都重複出現

## 核心設計：兩階段管線，不要混在一個prompt裡

當使用者要「持續追蹤+學習建議」時，優先拆成**兩個階段**而不是一個混合prompt：

1. **收集階段（Collector）**：只抓官方/第一方來源，保留來源品質標記，不做判斷、不下結論。
2. **分析階段（Analyzer）**：讀收集階段的輸出，轉成P1/P2/P3學習優先順序。

這樣拆的理由：資料品質問題（被擋、404、front-end渲染）跟判斷品質問題（技能排序對不對）分開，才能debug「這次建議差是資料爛還是判斷爛」；而且能讓原始證據留著可稽核，最後只把「精簡+有優先順序」的部分交給使用者看，不必每次都看到一堆連結。

## Stage A：收集（Collector）

### 預設監控公司池

`scripts/track_bigtech_signals.py`目前實際內建17家：台積電、聯發科、瑞昱、宏碁、趨勢科技、華碩、緯穎、台達電、友達、研華、光寶、廣達、和碩、英業達、鴻海、Google、NVIDIA。

可再擴充：ASML Taiwan、AMD、Intel Taiwan、Qualcomm、Microsoft、AWS等。

依使用者需求調整——公司池不是固定清單，原則是「能不能提供可驗證的官方職缺證據」，不是公司知名度。新增公司時記得同步更新這份清單，避免文件跟程式碼對不上。

### 執行

```
python3 scripts/track_bigtech_signals.py
```

這支腳本直接打各公司官方API/職缺頁（MediaTek tRPC、宏碁SuccessFactors頁、Trend Micro/Advantech的Workday API、AUO的job_list API、Google官方職缺頁、各公司官方RSS），輸出一份分公司列出職缺/訊號、並標明「可直接信任」vs「僅供人工入口」的markdown報告。沒有可用官方來源的公司會老實印失敗訊息，不會讓整支程式中斷。

若使用者要追蹤的公司不在腳本清單裡，先查該公司官方careers頁是不是有可用的API/RSS（見`reference/company-retrieval-notes.md`的判斷方法跟已知案例），再決定要不要擴充腳本，或先降級成「僅人工入口監控」。

### 來源分級（貫穿整個skill的核心規則）

- **Tier 1（可直接信任）**：官方職缺頁可解析職缺卡片、官方API（Workday/tRPC/SuccessFactors/Jobvite等穩定介面）、官方工程/產品RSS。
- **Tier 2（官方入口，證據不完整）**：官方招募頁但沒有穩定可解析清單、官方頁描述AI/平台方向但非職缺清單本身。
- **Tier 3（僅供人工複查）**：104搜尋連結、被擋（403/Cloudflare challenge）或前端渲染看不到職缺卡的頁面。

不要把Tier 1跟Tier 3當同等證據混在一起下結論。公司重要但頁面被擋，保留在監控清單但標「官方入口/證據不足」，不要假裝已整合。

### 存取被擋時的升級策略

1. 先試直接fetch/官方API路徑。
2. 被擋就試真實瀏覽器session/browser automation路徑（若環境有的話）。
3. 還是拿不到完整內容，用搜尋引擎索引摘要當低信心的方向性參考，並在報告中明講信心降級。
4. 持續性監控優先選「穩定」的存取路徑，不要選「最聰明但脆弱」的。
5. 見`reference/104-job-board-notes.md`關於104板特有的存取細節。

### 誠實紀律

不要在只有104搜尋入口、搜尋引擎索引片段、或官方品牌頁的情況下，宣稱已經拿到完整職缺覆蓋。證據不足就寫「本週證據不足」，不要硬湊。

## Stage B：分析（Analyzer）

讀Stage A的輸出（不要重新抓資料），做以下事：

### 1. 樣本量門檻
下強結論前至少要有15-30筆職缺證據。樣本太薄，只能給方向性參考並明講信心等級（high/medium/low confidence）。

### 2. 抽取可重用的招募訊號
從每則職缺只留：職缺家族、必備vs加分技能、框架/模型/基礎設施、年資帶（如有）、領域脈絡（LLM應用/資料平台/MLOps/CV-VLM/agent workflow）。不要只看標題，也不要被單一職缺裡的花俏關鍵字帶偏。

### 3. 正規化成能力群組（capability bucket）
不要逐字比對職缺標題（大公司對同樣工作內容命名差很多）。改用能力群組，例如：
- 軟體工程基礎（Python、API、backend、SQL、testing、Git）
- 資料與檢索（ETL、vector DB、embeddings、RAG、ranking）
- LLM應用（prompt engineering、tool calling、evals、guardrails）
- Agent/workflow orchestration（planning、tool use、multi-step automation、state/memory）
- 多模態/VLM（OCR、影像理解、文件解析）
- MLOps/serving（Docker、GPU inference、model serving、monitoring）
- 雲端與平台（AWS/GCP/Azure、k8s、觀測性）

多公司比對時見`reference/role-family-clustering.md`——核心規則是「比能力群不比職稱字串」，且職缺家族出現在≥3家公司才算「跨公司共通」，1-2家公司的高價值家族要另外標「集中層」而非灌水成市場共識。

### 4. 轉成學習優先順序
不要說「全部都要學」。用這個邏輯排序：
1. 先看哪些技能在最多職缺家族裡都出現——這是入場券技能。
2. 把「入場券技能」跟「專精技能」分開列。
3. Agent/VLM這類專精層，預設疊加在軟體工程+LLM基礎之上，除非樣本明顯指向不是這樣。
4. 標明某個熱門關鍵字在樣本裡是「常見/新興/小眾」。

### 5. 信心標註
樣本薄或只有間接證據（例如摘要而非完整職缺描述），要明講：
- high confidence：多則職缺重複出現
- medium confidence：有重複但樣本有限
- low confidence：小樣本/間接證據推論

## 輸出格式（依情境挑一種）

**完整分析格式**（一次性深度問答）：
1. 結論 — 現在真正值得學的方向
2. 市場常見技術群 — 分組列技能跟例子
3. 值得先補的能力 — 先學vs後學
4. 風險/不要誤判的地方 — 看似熱門其實還小眾的
5. 下一步 — 具體學習或監控計畫

**週報壓縮格式**（要固定重複投遞時用）：
```
1. 技能：...
   來源職缺：公司A / 職缺1；公司B / 職缺2
   推薦原因：...
2. 技能：...
   （最多列3-5個，證據薄就直接寫「本週證據不足」，不要硬湊）
```

**職缺家族雷達格式**（公司池夠大、想看趨勢時）：
```
職缺家族：...
技術棧：...
代表職缺：公司 / 職缺；公司 / 職缺
學習優先順序：P1 / P2 / P3
推薦原因：...
```
公司池分布不均時，切成「跨公司共通層」（≥3家公司佐證）+「高價值集中層」（1-2家公司但策略重要），不要硬湊成一份假的均勻清單。

## 檔案結構

```
SKILL.md
scripts/
  track_bigtech_signals.py   Stage A收集腳本，直接打各公司官方/第一方來源(API+RSS+可解析careers頁)，輸出markdown報告（stdlib only）
reference/
  104-job-board-notes.md         104職缺板存取細節與信心降級規則
  company-retrieval-notes.md     各公司官方來源存取方式(MediaTek tRPC/TSMC 403/Acer SuccessFactors/Workday系/AUO API等)
  role-family-clustering.md      跨公司職缺家族分群方法、兩層雷達格式
```

## 已知限制（誠實列出）

- 預設公司池以台灣大公司為主，是使用者原始情境下的設定，換題目/換國家要自己調整`scripts/track_bigtech_signals.py`裡的`COMPANIES`清單。
- 官方來源的可解析程度會隨時間變（公司改版官網、換API），`reference/company-retrieval-notes.md`裡的存取方式是特定時間點觀察到的結果，不是永久保證，要定期重新驗證。
- Stage B的分析仰賴LLM讀Stage A輸出後的判斷，不是決定性演算法，樣本薄的公司/職缺家族分類邊界可能不準。
- 104職缺板目前沒有穩定的機器可解析路徑，長期只能當人工複查入口，這是外部限制不是這個skill能解的。
