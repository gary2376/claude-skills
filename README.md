# claude-skills

自建 Claude Skills 庫，每個資料夾一個獨立可安裝的 skill。

## 收錄

- [resume-jd-checker](resume-jd-checker/) — 繁體中文履歷 x JD 關鍵字健檢
- [prompt-craft](prompt-craft/) — 模糊需求轉結構化 prompt，缺漏欄位主動反問

## 安裝

在終端機執行（或直接貼給你的 agent 執行，`<skill資料夾名>` 換成上面清單的名字）：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/<skill資料夾名>
```
會自動偵測目前的 agent（Claude Code、Codex、Cursor 等）裝到對應路徑，不限 Claude 專用。
