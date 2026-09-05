# Company-specific retrieval notes

Concrete source-handling patterns for the default company pool. These are examples of how each official source behaves, not universal truths — re-verify when a site changes.

## MediaTek 聯發科 — Tier 1（官方API可直接查）

- `https://careers.mediatek.com/` redirects to `/en`; naive fetches to `/en` or `/zh-tw` can loop with `307` because the site expects locale state. This is **not** a reason to downgrade MediaTek to manual-only.
- What works:
  1. Use a locale path such as `https://careers.mediatek.com/zh-tw/jobs`.
  2. Send a locale cookie: `NEXT_LOCALE=zh-tw`.
  3. Treat the HTML page as a discovery surface only — use the public tRPC endpoint for actual retrieval.
- Endpoint: `GET https://careers.mediatek.com/api/trpc/job.getJobs?batch=1&input=<urlencoded json>`
- API quirk: locale enum must be API form `zh_TW`, not page-locale form `zh-tw`.
- Payload shape:
  ```json
  {"0":{"json":{"locales":"zh_TW","page":1,"jobQueryInfo":{"keywords":["機器學習"],"relation":"AND"},
  "filters":{"categorys":[],"workExperiences":[],"locations":["0000009255","0000009256","0000073451","9031"],"programs":[]},
  "sortBy":"publishedDate","order":"DESC","limit":5}}}
  ```
- Taiwan location codes目前腳本(`MEDIATEK_TW_LOCATIONS`)實際使用：台北`0000009255`、新竹`0000009256`、竹北`0000073451`、台南`9031`。若之後在官方payload裡發現更多地區代碼，記得同步加進腳本常數，不要只改這份文件。
- Observed demand shape (example, re-verify over time): `機器學習`/`AI Runtime` keywords surfaced camera-AI/CV、AI application、AI runtime roles; `Linux`/`嵌入式` surfaced broader, more durable demand than flashy VLM-only terms.

## TSMC 台積電 — Tier 3（官方入口存在，機器抓取被擋）

- `https://careers.tsmc.com/` and `.../zh_TW/job-opportunities` return `403` to non-browser fetches.
- Do not claim TSMC has been "integrated" when the only verified fact is that the page exists but blocks scripted access.
- Keep the official URL in the report, labeled as browser-backed/manual-review monitoring. Only upgrade to machine-trusted after verifying a stable public endpoint.

## Google — Tier 1（官方頁可直接解析）

- Official Taiwan careers results page is directly parseable enough to extract concrete openings. Prefer it over generic search results whenever available. Currently the strongest example of a directly-parseable big-tech source in this pool.

## NVIDIA — Tier 2（混合）

- Official Taiwan careers landing page is reachable, but job cards are front-end rendered — keep as official manual-review/search entry unless a stable job API is found.
- Official blog/RSS is high-value for direction signals even when the job list itself isn't machine-parseable.
- Example pure-software role families seen live: GPU software program management, systems software engineer, data center system software test/tooling, SOC system software — don't bucket NVIDIA Taiwan as hardware-only.

## Realtek 瑞昱 — Tier 2（官方站可進，職缺清單不穩定）

- Official site returns HTTP 200 but a stable, directly-parseable job-list page has not been established. Keep as official entry point only until a stable jobs page is confirmed.

## AUO 友達 — Tier 1（官方API可直接查）

- Career site: `https://career.auo.com/`, useful endpoints: `/job_list`, `/job_list/GetJobList`.
- Strong signal for pure-software AI roles — don't treat as a branding page or 104 mirror.
- Example role families seen live: AI application engineer, backend-heavy full-stack + AI/data integration, AI security/compliance analyst, AI solutions engineer.
- Common stack hints seen live: C#, Python, VueJS, Tableau/Power BI, SQL/DataLake, AWS/Azure/Databricks/PySpark.

## ASUS 華碩 — Tier 2（招募頁有hint，深層頁常被擋）

- Brand/recruiting pages: `https://ehr.asus.com/chinese/`, `https://recruit.asus.com/Home/`. The recruiting microsite exposes job-interest hints (including AI-related tracks in campus/intern context), but the deeper recruit site may be blocked by CloudFront. Treat as **partial evidence** unless a session successfully retrieves stable listings.

## Acer 宏碁 — Tier 1（官方SuccessFactors頁可直接解析）

- `ACER_ALL_JOBS_URL`（SuccessFactors的All Jobs頁）可直接解析職缺卡片，不是Workday。

## Trend Micro 趨勢科技 / Advantech 研華 — Tier 1（官方Workday API）

- 兩家都跑在Workday上，first-party job-list JSON端點：`*.wd3.myworkdayjobs.com/wday/cxs/.../External/jobs`。Prefer these over 104 whenever the company runs on Workday.

## Cross-cutting reporting rule

Do not force fake symmetry across companies. If only one or two companies currently yield a directly verifiable opening list, show a verified block for those and official/manual-review entry links for the rest, with a short confidence note explaining the difference. That is better than pretending all companies have equal signal quality.
