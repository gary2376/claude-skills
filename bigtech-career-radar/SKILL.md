---
name: bigtech-career-radar
description: "Use when the user wants to monitor official hiring signals for any industry/companies and turn them into a learning-priority roadmap — e.g. '幫我看台積電/聯發科/Google最近在找什麼AI職缺', '追蹤心理師職缺', '保險業職缺該學什麼技能', or wants a recurring digest of this. Config-driven: ships an AI/Taiwan-bigtech example plus a psychologist and an insurance example, and generalizes to any industry via a JSON config (company list + keywords) using three reusable adapters (Workday, WordPress association/union job boards, generic Chinese-labeled job pages) or a company-specific one written the same way MediaTek/Acer/AUO/Google's were. Core differentiator: refuses to launder blocked pages, search-engine snippets, or job-board noise into confident hiring-trend claims — every conclusion is tagged with its evidence tier."
---

# 職缺訊號雷達（config驅動，不限產業）

追蹤任何產業/公司的官方職缺訊號，轉成有優先順序的學習路線圖。核心差異化：市面上多數「職缺爬蟲/技能雷達」是把搜尋引擎結果或104關鍵字命中直接當成市場需求，這個skill把「來源可信度」當一等公民——官方API/官方頁 vs 人工入口 vs 被擋的頁面，分開處理，被擋就老實寫被擋，不腦補技能方向。

**不限AI/科技業**：公司清單、關鍵字、輸出標題全部搬進`config.json`，換產業不用改程式碼。內建3份範例設定檔（AI/台灣大公司、台灣臨床心理師、台灣壽險業），三個都已經真的跑過、有真實職缺資料驗證過。

這套三層來源分級跟兩階段管線設計，是從實際反覆執行、觀察各公司來源穩不穩定之後整理出來的規則，不是憑空設計的規則。

## 何時觸發

使用者問：
- 現在大公司AI/軟體職缺在找什麼技術？（或任何其他產業：心理師、保險、室內設計⋯）
- 我該學什麼才能進某家公司/某個領域？
- 幫我定期追蹤職缺市場，看技能需求有沒有變化
- 把一堆職缺整理成實際的學習路線
- 想追蹤一個全新的產業/公司池，判斷哪些來源值得監控
- 想知道哪些職缺家族在多家公司都重複出現

## 核心設計：兩階段管線，不要混在一個prompt裡

當使用者要「持續追蹤+學習建議」時，優先拆成**兩個階段**而不是一個混合prompt：

1. **收集階段（Collector）**：只抓官方/第一方來源，保留來源品質標記，不做判斷、不下結論。
2. **分析階段（Analyzer）**：讀收集階段的輸出，轉成P1/P2/P3學習優先順序。

這樣拆的理由：資料品質問題（被擋、404、front-end渲染）跟判斷品質問題（技能排序對不對）分開，才能debug「這次建議差是資料爛還是判斷爛」；而且能讓原始證據留著可稽核，最後只把「精簡+有優先順序」的部分交給使用者看，不必每次都看到一堆連結。

## Stage A：收集（Collector）

### config驅動，換產業不用改程式碼

`scripts/track_signals.py`不寫死任何公司/關鍵字，全部從`--config`指定的JSON檔讀。內建3份範例：

```
python3 scripts/track_signals.py --config config.ai-taiwan.json        # AI/台灣大公司(預設)
python3 scripts/track_signals.py --config config.psychologist-tw.json  # 台灣臨床心理師
python3 scripts/track_signals.py --config config.insurance-tw.json     # 台灣壽險業
```

三份都真的跑過、抓到真實職缺資料（不是只有架構沒驗證）。

### config.json結構

```json
{
  "title": "報告標題",
  "intro_notes": ["開頭說明文字"],
  "companies": [
    {"name": "公司/機構名", "adapter": "解析器名稱或manual", "career_url": "...", "notes": ["..."], "adapter_params": {...}}
  ],
  "official_feeds": [{"label": "...", "url": "RSS網址", "require_any": [...], "block_any": [...]}],
  "job_focus_keywords": ["篩選職缺用的關鍵字"],
  "trend_keywords": ["篩選RSS趨勢用的關鍵字"],
  "focus_area_buckets": [["分類標籤", ["關鍵字1", "關鍵字2"]]]
}
```

### 7種解析器（adapter）

**3個通用型，換公司只要改config參數，不用寫新程式碼：**
- `workday`：用Workday當徵才系統、且網址是`{tenant}.wd3.myworkdayjobs.com/.../External/jobs`這個已驗證格式的公司，參數只要`tenant`(租戶名稱)+`search_text`+`location_filters`。Workday本身橫跨產業(零售/金融/製造/科技都有公司用)，但不同公司的Workday部署可能用不同shard(wd1~wd5)或不同site路徑(非External)，套用新公司時要先確認網址格式吻合，不吻合就要調整`parse_workday_jobs()`裡寫死的host/path。範例：趨勢科技、研華。
- `wordpress_category`：公會/學會/協會常見的WordPress徵才專區，抓分類頁的entry-title清單，逐篇讀取內容。範例：台灣臨床心理學會徵才專區。
- `labeled_html_page`：單一頁面裡用中文欄位標籤（機關名稱/職稱/資格條件/工作內容/工作地點等常見別名）重複列出多筆職缺的公司官網常見格式。範例：台灣人壽「一般職缺」頁。

**4個公司專屬型，示範怎麼寫一支新的，換公司不一定能直接套：**
- `mediatek_trpc`（聯發科官方tRPC API）、`acer_successfactors`（宏碁SuccessFactors頁）、`auo_joblist`（友達自家API）、`google_careers`（Google官方職缺頁HTML）。

**`manual`**：沒有可用API/穩定解析格式的公司，只印官方連結當人工複查入口，不硬解析。

### 幫使用者換新產業/公司池時怎麼做

1. 先問清楚目標產業、關鍵字、想追蹤的機構/公司名單。
2. 對每個目標，先查官方職缺頁是不是Workday(`*.myworkdayjobs.com`)或WordPress徵才專區——是的話直接套`workday`/`wordpress_category`，只要填參數。
3. 都不是的話，實際curl/fetch該頁面看內容：能抓到結構化中文欄位（職稱/資格條件/工作內容這類）就試`labeled_html_page`；被403/WAF/CAPTCHA擋住、或整頁是JS渲染空殼，直接標`manual`，不要嘗試繞過反爬蟲機制（可能涉及違反對方服務條款，也不是這個skill的目標）。
4. 寫一份新的`config.<產業>.json`，跑`python3 scripts/track_signals.py --config config.<產業>.json`實際驗證有沒有抓到真實資料，不要只憑猜測就交付。
5. 見`reference/company-retrieval-notes.md`已知案例(MediaTek/TSMC/Google/NVIDIA/Acer/Workday系公司)的判斷方法。

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
  track_signals.py              Stage A收集腳本，config驅動，7種adapter（stdlib only）
  config.ai-taiwan.json         範例1：AI/台灣大公司(17家，跟舊版行為一致)
  config.psychologist-tw.json   範例2：台灣臨床心理師(學會徵才專區)
  config.insurance-tw.json      範例3：台灣壽險業(公司官網職缺頁)
reference/
  104-job-board-notes.md         104職缺板存取細節與信心降級規則(適用任何被擋的類104平台)
  company-retrieval-notes.md     各公司官方來源存取方式(MediaTek tRPC/TSMC 403/Acer SuccessFactors/Workday系/AUO API等)
  role-family-clustering.md      跨公司職缺家族分群方法、兩層雷達格式
```

## 已知限制（誠實列出）

- 3份範例設定檔都真的驗證過能抓到真實職缺，但只驗證了各自設定檔裡列的那幾個來源——換到別的公司/機構，`workday`/`wordpress_category`理論上該通用，`labeled_html_page`的中文欄位別名清單(`FIELD_ALIASES`)是從2個真實案例(台灣臨床心理學會、台灣人壽)歸納出來的，換一個網站的欄位命名習慣不同就可能抓不到，需要重新驗證、必要時擴充別名清單。
- 官方來源的可解析程度會隨時間變（公司改版官網、換API），`reference/company-retrieval-notes.md`裡的存取方式是特定時間點觀察到的結果，不是永久保證，要定期重新驗證。
- 遇到CAPTCHA/企業級WAF/純JS渲染的頁面（104、1111人力銀行、國泰/富邦人壽、NVIDIA台灣職缺頁等都屬此類），不要嘗試用無頭瀏覽器等方式繞過——這已經超出「解析可公開存取的HTML」範疇，可能涉及違反對方服務條款，直接標`manual`人工複查即可。
- Stage B的分析仰賴LLM讀Stage A輸出後的判斷，不是決定性演算法，樣本薄的公司/職缺家族分類邊界可能不準。
- 104職缺板目前沒有穩定的機器可解析路徑，長期只能當人工複查入口，這是外部限制不是這個skill能解的。
