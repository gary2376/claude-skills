# prompt-craft

把「幫我寫封信」這種模糊需求，轉成 AI 聽得懂的結構化 prompt。不是單向轉換工具——會先反問你漏講了什麼，
不會自己亂猜。

## 安裝

貼給 Claude：
```
幫我安裝這個 Claude Skill：https://github.com/gary2376/claude-skills/tree/master/prompt-craft
複製到 ~/.claude/skills/prompt-craft
```

## 功能
- 偵測需求裡缺了角色、背景、格式、受眾語氣、範例、限制這 6 個維度中的哪些
- 主動反問缺漏的部分，不會直接臆測（除非你說「不用問了直接猜」）
- 每補一個欄位附一句「為什麼要補這個」，附權威來源依據
- 職場書信、會議紀錄、資料分析需求、客服回覆 4 個場景有在地化優先序

## 使用

裝好後直接貼你想請 AI 做的模糊需求，或問「這個 prompt 要怎麼寫比較好」。
