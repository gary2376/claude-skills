# claude-skills

自建 Claude Skills 庫，每個資料夾一個獨立可安裝的 skill。

## 目前收錄

- [resume-jd-checker](resume-jd-checker/) — 繁體中文履歷 x JD 關鍵字健檢，中英雙語比對 + AI 用語偵測

## 安裝（推薦：直接叫 Claude 幫你裝）

打開 Claude Code 或 Claude Desktop，貼上這段話（把 `<skill資料夾名>` 換成上面清單裡的名字，例如 `resume-jd-checker`）：

```
幫我安裝這個 Claude Skill：https://github.com/gary2376/claude-skills/tree/master/<skill資料夾名>
複製到 ~/.claude/skills/<skill資料夾名>
```

Claude 會自己處理下載跟複製，裝完直接可以用，不用自己跑指令、不用改路徑。

<details>
<summary>其他安裝方式（手動）</summary>

用 [skills CLI](https://github.com/vercel-labs/skills)：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/<skill資料夾名>
```
（monorepo 子資料夾要用完整 GitHub tree URL，`owner/repo/子資料夾` 這種寫法不會生效）

或手動把該 skill 資料夾整個複製進 `~/.claude/skills/`。
</details>

## 新增 skill

在 repo 根目錄新增一個資料夾，內含該 skill 自己的 `SKILL.md` + `README.md`，同結構獨立運作，互不依賴。完成後回來這份 README 加一行連結。
