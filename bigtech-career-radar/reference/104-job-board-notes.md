# 104 job-board access notes

Use these notes when the user wants 104-based market analysis or recurring monitoring.

## Reality check

Direct plain-HTTP fetches to 104 search/AI pages usually return anti-bot protection rather than job content. Treat 104 as a **manual review entry link**, not a machine-trusted evidence source, unless you can read a real structured 104 result page directly (e.g. via a real browser session).

## Practical escalation order

1. Try first-party search/result pages via a plain fetch.
2. If blocked, try a real local browser session (if the environment has one available) and verify the page actually loaded (check title/URL) before investing in extraction work.
3. If full text extraction is still unavailable, indexed snippets from search engines are an acceptable low-confidence directional fallback — but say so explicitly.
4. If the user wants weekly updates now, create the recurring job anyway, but describe it as a **104 AI job-signal monitor**, not a full 104 posting miner.
5. For recurring monitoring, prefer whichever access path is *stable* over whichever is *cleverest*.

## Reporting rule

If the analysis had to rely partly on search-index snippets instead of full posting bodies, explicitly downgrade confidence and avoid making overly specific hiring-trend claims.
