# prompt-craft 研究彙整

跨7類來源(官方廠商文件、學術survey、Reddit社群、繁中/簡中媒體、企業調查、框架比較站、既有競品)彙整,供撰寫 SKILL.md 用。不要每次重查,直接查表。

## 一、框架比較總表

| 框架 | 組成 | 適用場景 | 來源類別數 |
|---|---|---|---|
| CO-STAR | Context, Objective, Style, Tone, Audience, Response format | 內容/文案類(信件、貼文、文案),語氣受眾要求高的任務 | 5+(比較站群) |
| RTF | Role, Task, Format | 簡單直接任務 | 多(比較站群) |
| RACE | Role, Action, Context, Execute | 求快、不重格式包裝的任務 | 多(比較站群) |
| PTCF | Persona, Task, Context, Format | Google Gemini官方推薦結構 | 官方一手(ai.google.dev, Google Workspace) |
| CRISPE | Capacity/Role, Insight, Statement, Personality, Experiment | 需要語氣人格設定、想跑多個變化方案 | Medium/Penlify/TalentGro |
| RISEN | Role, Instructions, Steps, End goal, Narrowing | 複雜多步驟任務,想看中間推理過程 | AskSmarter/Promplify |
| ICIO | Identity, Context, Input, Output | 學術survey收錄的標準化分類之一 | 《The Prompt Report》(arXiv 2406.06608) |
| Anthropic官方結構(非縮寫) | 明確角色/任務、multishot範例、chain-of-thought、XML標籤分隔、長脈絡、明訂success criteria | Claude系列模型最佳實務 | 官方一手(docs.anthropic.com) |
| OpenAI官方原則(非縮寫) | 具體詳細描述情境/目標/格式、拆解複雜任務、語氣形容詞引導、迭代修正 | ChatGPT/API通用 | 官方一手(help.openai.com) |
| 中文六要素(知乎) | 角色、背景、任務、格式、限制、示例 | 中文語境職場任務,概念上等同CO-STAR/RTF融合版 | 知乎專欄《提示詞6要素》 |
| Prompt Report學術分類 | 58種prompting技巧總表(zero-shot/few-shot/CoT/ToT/self-consistency…) | 學術完整度最高的分類基礎,非給終端使用者直接套用 | arXiv 2406.06608 + promptingguide.ai(3M+學習者) |

**高信度結論**:各框架名稱不同,但收斂到同一組核心維度——**角色/身分、任務目標、背景脈絡、輸出格式、語氣受眾、範例/限制**。CO-STAR、RTF、PTCF、CRISPE、中文六要素本質是這組維度的不同排列組合,不是互斥選擇。skill不必綁死單一框架名稱,應該直接用這組共同維度做欄位設計。

## 二、非技術使用者常見錯誤(依來源數排序)

| 錯誤模式 | 確認來源類別 | 信度 |
|---|---|---|
| 單一句話「願望型」指令,沒講清楚具體任務(例:「幫我寫封信」「改善我的履歷」) | OpenAI官方、知乎(「需求太像一句願望,不是任務說明」)、Reddit(dev.to系列)、CSDN、Zapier | 高(5類來源) |
| 沒講輸出格式/長度限制 | Google PTCF官方、Anthropic官方(success criteria)、CSDN五要素 | 高(3類來源+2個官方一手) |
| 沒講受眾/語氣 | CO-STAR、Google PTCF(Persona)、CSDN | 中高(3類來源) |
| 沒給範例(few-shot) | Anthropic官方(multishot顯著提升品質)、DAIR.AI Guide、知乎六要素 | 中高(3類來源,含1個官方一手) |
| 複雜任務沒拆解成步驟 | RISEN框架、OpenAI官方(break down complex tasks) | 中(2類來源) |
| 不會迭代,一次定生死就放棄 | OpenAI官方(iterative refinement)、Reddit(accepting first explanation without refinement) | 中(2類來源) |
| 一次塞過多資訊/多任務混在一起 | Reddit社群共識(drowning the model)、Anthropic研究觀察到的instruction amnesia現象(長prompt中模型會忽略部分限制) | 中(2類來源,但方向是「反效果」提醒,非skill核心機制) |

**單一來源、僅供參考,不作為設計依據**:「反問法」入門技巧(vocus單篇文章)——使用者自己主動問AI「你還需要哪些背景資訊」,概念上跟本skill想做的「AI主動反問使用者」方向一致,但只有1篇來源,列為佐證而非決策依據。

## 三、實證痛點數據

| 數據 | 來源 |
|---|---|
| 35%員工完全沒受過任何AI訓練;受過訓練者中只有18%覺得「準備好能獨立作業」;85%員工說訓練內容對自己實際職務沒幫助 | DataCamp《The AI Skills Gap in 2026》 |
| 僅34%員工對「把工作任務拆解成AI可處理的步驟」(task decomposition)有信心——換句話說,近三分之二員工不會拆解需求 | LinkedIn/TalentLMS系列2026職場學習報告 |
| 訓練缺口前三名:缺「具體職務範例」(51%)、缺「練習題」(48%)、缺「應用時間」(38%) | 同上,IDC/Workera $5.5兆技能缺口報告 |
| 44%美國職場工作者說公司沒有明確AI政策,或不確定有沒有 | 2026企業AI採用調查(WRITER彙整) |
| 「矽天花板」現象:主管級75%常態用GenAI,第一線員工只有51% | BCG AI at Work調查 |

**最有力的一條**:34%員工對task decomposition有信心——這代表問題核心不是「不會打字下指令」,是「不知道怎麼把腦中模糊的工作需求拆解成AI聽得懂的具體任務」。這條直接支撐本skill的核心機制設計方向(見下方「最重要發現」)。

## 四、既有競品/工具掃描

查到多個已上線、功能高度重疊的獨立工具:**SurePrompts、GetEasyPrompt、PromptBuilder.cc、zalt.me/tools/prompt-builder、structuredprompt.com**。共同模式:使用者填一段plain-English描述(任務/受眾/語氣),工具組裝成含角色/脈絡/格式的結構化prompt。

**這是本轉向最大的風險點**——「輸入一句話→吐出結構化prompt」這個動作本身已經是紅海,多個SaaS做得成熟。如果skill只做這件事,等於重造輪子,portfolio上會被一眼看穿。

**差異化空間(排除掉已被做爛的部分後,剩下的縫隙)**:
1. **這些工具全部是單向轉換,不會反問**——預設使用者自己已經知道角色/受眾/語氣要填什麼,只是懶得排版。但真正職場新手的困境(呼應第三節34%數據)是「不知道自己漏講了什麼」,不是「知道但懶得寫」。本skill該做、這些工具沒做的:偵測缺漏欄位後用白話主動反問,而非丟一張空表單要使用者自己填。
2. **全部是獨立網站**,要離開原本工作對話、切換分頁、複製貼回——裝成Claude Skill可以直接在原本對話裡完成,不用换工具。
3. **全部沒有在地化**——沒有針對繁中職場溝通慣例(例如中文email正式程度分級、跟主管請假/跟客戶道歉的用語慣例)特化。
4. **全部是黑箱輸出**,不解釋「為什麼幫你補這個欄位」——呼應第三節「51%缺具體職務範例、48%缺練習題」的訓練缺口,skill可以附一句「為什麼這樣補」的教學提示,做成教育型工具而非純轉換工具。

**結論**:核心差異化不能放在「轉換」這個動作本身,要放在「互動式反問補缺漏」+「繁中職場情境在地化模板」+「教學說明」。純黑箱一次轉換已經被做爛,這條路線不值得重做。

## 五、引用依據表(給 SKILL.md 開發用)

給建議/補全prompt時,若命中以下情況,附上依據來源,不要每次重查整份文件,直接查這張表:

| 命中情況 | 依據來源 |
|---|---|
| 只有一句話願望型指令,沒有具體任務說明(例:「幫我寫封信」) | ⭐ OpenAI官方Prompt Engineering Best Practices——具體詳細描述情境與目標;知乎《提示詞6要素》——需求太像一句願望,不是任務說明 |
| 沒講輸出格式/長度 | ⭐ Google Gemini官方PTCF框架(Format維度);Anthropic官方Prompt Engineering指南——明確定義success criteria |
| 沒講受眾/語氣 | CO-STAR框架(新加坡GovTech推廣)——Tone與Audience為必要維度;Google PTCF——Persona |
| 沒給範例 | ⭐ Anthropic官方——multishot prompting顯著提升輸出品質與一致性;DAIR.AI Prompt Engineering Guide——few-shot prompting |
| 任務複雜但沒拆解步驟 | RISEN框架——Steps顯示中間推理階段;OpenAI官方——break down complex tasks into smaller steps |
| 一次塞了過多資訊/多任務混在一起 | Anthropic研究觀察——長prompt中模型會出現instruction amnesia(忽略部分限制);Reddit r/PromptEngineering社群共識——drowning the model反而降低輸出品質 |
| 使用者不知道自己缺了什麼資訊(根本原因,非單次prompt的錯字/格式問題) | ⭐ LinkedIn/TalentLMS 2026職場學習報告——僅34%員工對task decomposition有信心,51%缺乏職務相關具體範例 |

引用時格式:「這是 [具體問題] —— 依據 [人物/機構/框架]:[核心主張]」,一句話帶過,不要整段複製來源介紹。找不到對應的,不要硬套引用湊數。
