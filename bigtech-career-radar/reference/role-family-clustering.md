# Cross-company role-family clustering

Use this when the user asks things like "哪些公司都有類似職缺？"、"最多公司重複出現的職缺是什麼？"、or wants a broad company pool turned into a decision-useful map.

## Core rule: don't compare literal job titles

Large companies label similar work very differently — `AI Engineer`, `Applied AI Software Engineer`, `AI Runtime Engineer`, `Software Engineer, Pixel Camera`, and `Automation Engineer` may overlap in capability surface even when titles differ. Comparing literal titles undercounts true cross-company overlap.

## Method

1. Collect machine-trusted official evidence first (official careers pages/APIs/RSS). Downgrade blocked or noisy sources (104 behind a challenge page, search-engine snippets) — they're too noisy for strong overlap claims.
2. Normalize postings into role-family / capability buckets, not title strings.
3. Count how many distinct companies appear in each bucket.
4. Present overlap as capability families, not fake precision around exact title sameness: `最多公司共同出現的其實不是完全相同職稱，而是同一類能力群。`

## Default bucket set

- AI / ML / Runtime
- Platform / Cloud / Release / Automation
- Software / Applied Engineering
- Embedded / Firmware / Edge AI
- Silicon / Verification / Test
- Product / PM / Strategy

For a "pure software only" scope, further group into: AI application integration / backend+full-stack AI or data integration / data-analytics-AI enablement / ML platform-inference-runtime-agent systems / system software for AI products (only if clearly software-centric). Deprioritize manufacturing, hardware validation/packaging/process, firmware-only roles unless the user explicitly asks for them.

## Two-tier radar (when a flat list would mislead)

Switch from a flat top-N list to a two-tier structure when the output looks too concentrated in one or two companies, or the pool is large but evidence is uneven:

**跨公司共通層** — role families genuinely repeated across ≥3 companies with official/parseable evidence and similar work shape (not just similar buzzwords). Example: platform/cloud/backend software, security product software, release/automation/diagnostics tooling.

**高價值集中層** — strategically important families concentrated in 1–2 companies, kept visible without pretending they're broad market consensus. Example: Applied AI software concentrated at one company, ML/CV/runtime roles concentrated at another.

If only 1–2 common-layer families survive after filtering, that's acceptable — the lesson is that market evidence is uneven, not that the summary should be padded.

## Output shape

1. 結論
2. 可直接信任的公司樣本（company pool size, how many have direct evidence, which are monitoring-only)
3. 最多公司共同出現的職缺家族 / 能力群（top families, representative examples across companies)
4. 不要誤判的地方
5. 下一步 / 學習優先順序

Always explain concrete work content (systems they build, platforms they integrate with, model/runtime/data work performed), not just title or buzzword labels.
