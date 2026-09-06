# youtube-content

把YouTube影片轉成摘要/串文/部落格文章的Claude Skill。核心差異化：內容是靠腳本(`youtube-transcript-api`)真的抓字幕，LLM只負責把真實逐字稿重新排版，不會只憑標題/縮圖腦補內容。

## 安裝

在終端機執行（或直接貼給你的 agent 執行）：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/youtube-content
```
會自動偵測目前的 agent（Claude Code、Codex、Cursor 等）裝到對應路徑，不限 Claude 專用。

## 功能

- 支援任何YouTube網址格式（一般連結、youtu.be短連結、shorts、embed、live、純video ID）
- 6種輸出格式：章節列表、摘要、章節摘要、Twitter/X串文、部落格文章、金句摘錄
- 找不到字幕/影片不存在時乾淨回報錯誤，不會crash

## 使用

裝好後直接貼YouTube連結給agent，說「幫我摘要這部影片」「把這個轉成部落格文章」「列出章節」即可。

## 範例

**輸入**：貼一支中文podcast連結，說「幫我摘要這部影片」

**輸出（節錄，真實逐字稿摘要出來的）**
> 前Google執行長Eric Schmidt在訪談中拋出一個假設：若中國比美國早半年達到「超級智慧」(ASI)，美國會不會轟炸中國的資料中心？節目主持人從這個假設出發，拆解美中AI競賽的三個內部矛盾：晶片管制反而刺激中國自研演算法並轉向開源；美國一邊要贏得AI競賽，一邊卻刪減大學研究經費逼走人才；美國需要盟友打群架才有勝算，但單邊主義政策反而在傷害盟友信任。

## 已知限制

只支援有字幕（人工或自動生成）的影片，沒有語音轉文字備援。這個skill只處理單支影片的即時需求，不含「每天自動抓頻道新影片」這類常駐排程管線（追蹤清單/回填順序/去重狀態這些需要另外建置，規模大很多，不在這個skill範圍內）。
