# claude-skills

自建 Claude Skills 庫，每個資料夾一個獨立可安裝的 skill。

## 收錄

- [resume-jd-checker](resume-jd-checker/) — 繁體中文履歷 x JD 關鍵字健檢
- [prompt-craft](prompt-craft/) — 模糊需求轉結構化 prompt，缺漏欄位主動反問
- [dating-profile-checker](dating-profile-checker/) — 交友軟體自介健檢，依平台跟目標給對應建議
- [bigtech-career-radar](bigtech-career-radar/) — 追蹤任何產業職缺訊號(config驅動，內建AI/心理師/保險三範例)，分級來源可信度，轉成學習優先順序
- [youtube-content](youtube-content/) — YouTube影片轉摘要/串文/部落格文章，真實逐字稿驅動不腦補

每個skill都只產出標準markdown，不綁定特定知識庫工具——搭配任何llm-wiki實作（例如[Karpathy的LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)及其社群實作，如[Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki)、[atomicstrata/llm-wiki-compiler](https://github.com/atomicstrata/llm-wiki-compiler)）都能直接把輸出當來源餵進去，不用額外轉檔。

## 安裝

在終端機執行（或直接貼給你的 agent 執行，`<skill資料夾名>` 換成上面清單的名字）：
```
npx skills add https://github.com/gary2376/claude-skills/tree/master/<skill資料夾名>
```
會自動偵測目前的 agent（Claude Code、Codex、Cursor 等）裝到對應路徑，不限 Claude 專用。

## 各skill怎麼用

**resume-jd-checker** — 貼履歷文字/PDF + 想投的JD，或問「這句話是不是太AI了」。
```
幫我看這份履歷符不符合這個JD：[貼履歷] [貼JD連結或文字]
```

**prompt-craft** — 貼你想請AI做的模糊需求，缺什麼欄位它會反問，不會亂猜。
```
幫我寫封信跟主管請假
→ skill反問：想請幾天假、什麼原因、什麼語氣？
```

**dating-profile-checker** — 貼自介文字，說明平台跟目標。
```
這是我的Tinder自介，想認真找對象：「熱愛生活，喜歡旅行、美食...」
```

**bigtech-career-radar** — 直接問想追蹤的產業/公司，沒有現成config就請agent幫你建一份。
```
幫我追蹤台灣臨床心理師職缺，該學什麼技能
幫我看台積電/聯發科/Google最近在找什麼AI職缺
```

**youtube-content** — 貼YouTube連結，說要什麼格式。
```
幫我把這部影片轉成摘要：https://youtube.com/watch?v=xxx
幫我列出這支podcast的章節
```

## 延伸玩法：搭配LLM Wiki做技能地圖

`bigtech-career-radar`跟`youtube-content`都只產出乾淨markdown，可以直接當來源餵進任何Karpathy LLM Wiki實作，變成一套「找方向→補教材→留存知識」的複利流程：

1. **bigtech-career-radar** 抓出你想轉職/學習的領域目前需要什麼技能（P1/P2/P3學習優先順序）。
2. 針對排出來的技能，找對應教學影片/podcast，用 **youtube-content** 轉成逐字稿+摘要。
3. 把兩邊的輸出都丟給你的LLM Wiki（例如`karpathy-llm-wiki`skill）當ingest來源——career-radar的輸出會變成「這個領域需要什麼」的concept頁，youtube-content的摘要會變成對應的學習筆記，兩邊自動互相cross-reference。
4. 之後每次追蹤到新職缺、看完新教學影片，重複ingest，wiki持續累積、不會每次都從零開始——這就是「知識再利用」的複利效果，不是查完就丟。

三個skill都是獨立的，不互相依賴，也可以只用其中一個。
