# claude-skills

自建 Claude Skills 庫，每個資料夾一個獨立可安裝的 skill。

## 收錄

- [resume-jd-checker](resume-jd-checker/) — 繁體中文履歷 x JD 關鍵字健檢
- [prompt-craft](prompt-craft/) — 模糊需求轉結構化 prompt，缺漏欄位主動反問
- [dating-profile-checker](dating-profile-checker/) — 交友軟體自介健檢，依平台跟目標給對應建議
- [bigtech-career-radar](bigtech-career-radar/) — 追蹤大公司AI職缺訊號，分級來源可信度，轉成學習優先順序
- [youtube-content](youtube-content/) — YouTube影片轉摘要/串文/部落格文章，真實逐字稿驅動不腦補

每個skill都只產出標準markdown，不綁定特定知識庫工具——搭配任何llm-wiki實作（例如[Karpathy的LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)及其社群實作）都能直接把輸出當來源餵進去，不用額外轉檔。

## 安裝

在終端機執行（或直接貼給你的 agent 執行，`<skill資料夾名>` 換成上面清單的名字）：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/<skill資料夾名>
```
會自動偵測目前的 agent（Claude Code、Codex、Cursor 等）裝到對應路徑，不限 Claude 專用。
