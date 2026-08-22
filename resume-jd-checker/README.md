# resume-jd-checker

繁體中文履歷 x JD 關鍵字健檢 Claude Skill，支援中英雙語比對（JD 寫 Machine Learning、履歷寫機器學習也抓得到）。

## 安裝

在終端機執行（或直接貼給你的 agent 執行）：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/resume-jd-checker
```
會自動偵測目前的 agent（Claude Code、Codex、Cursor 等）裝到對應路徑，不限 Claude 專用。

## 功能
- 中英雙語關鍵字比對（JD vs 履歷，目前科技/AI 產業支援最完整）
- AI 用語偵測（GPTism / 中文 AI 味用詞）
- 照片、頁數、格式、自傳等固定建議規則，附權威來源依據

## 使用

裝好後直接在 Claude 對話貼履歷 + JD，或問「幫我看這份履歷符不符合這個 JD」。

## 範例

**輸入**
JD 片段：「熟悉 Machine Learning、具備跨部門溝通能力」
履歷片段：「熟悉機器學習，個性樂觀積極，善於溝通」

**輸出（節錄）**
> ✅ 關鍵字比對：JD 的 Machine Learning 對應到履歷的「機器學習」，已命中（中英雙語比對）。
> ⚠️ AI 用語警示：「個性樂觀積極」「善於溝通」——只有形容詞、沒有可驗證內容，依據 104職場力《10大常見NG錯誤》，建議改成具體事蹟（例如帶過幾人的專案、跨了哪些部門）。
