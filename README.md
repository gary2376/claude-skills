# claude-skills

自建 Claude Skills 庫，每個資料夾一個獨立可安裝的 skill。

## 目前收錄

- [resume-jd-checker](resume-jd-checker/) — 繁體中文履歷 x JD 關鍵字健檢，中英雙語比對 + AI 用語偵測

## 安裝單一 skill

```
npx skills add gary2376/claude-skills/<skill資料夾名>
```

或直接把該 skill 資料夾複製進 Claude Code / Claude Desktop 的 skills 目錄。

## 新增 skill

在 repo 根目錄新增一個資料夾，內含該 skill 自己的 `SKILL.md` + `README.md`，同結構獨立運作，互不依賴。完成後回來這份 README 加一行連結。
