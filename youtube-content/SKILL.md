---
name: youtube-content
description: "Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video — e.g. 'summarize this video', 'turn this talk into a blog post', 'give me the chapters for this'. Fetches the real transcript via a deterministic script and reformats it into chapters, summaries, threads, blog posts, or quotes, grounded in what was actually said rather than invented from the title/thumbnail."
---

# YouTube Content Tool

Extract transcripts from YouTube videos and convert them into useful formats (chapters, summaries, threads, blog posts, quotes). The transcript itself is fetched by a small deterministic script — the LLM's job is to reformat that real transcript text, not to guess at the video's content from its title or thumbnail.

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video.

## Setup

```bash
pip install youtube-transcript-api
```
(or `uv pip install youtube-transcript-api` if your environment uses `uv`)

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

See `reference/output-formats.md` for worked examples of each format.

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`, with no `--language` on the first try.
2. **Validate and retry on failure** — the right retry direction depends on which error you get, they are opposite:
   - `"No transcript found. Try specifying a language..."` (the no-language default call couldn't pick a track) → **add** an explicit `--language` list. Guess from context: the video's apparent language plus `en` as a fallback (e.g. a Chinese-language video: `--language zh-TW,zh-Hant,zh,en`). Confirmed in testing: some videos' transcript simply isn't found by the library's own default track selection, but resolve fine once you name the language(s) explicitly.
   - You already passed `--language` and it came back empty/wrong → **drop** `--language` (or broaden the list) to fall back to whatever transcript is actually available, then note the real language to the user.
   - Either way still empty after retrying → tell the user the video likely has transcripts disabled (confirmed real case: some channels never enable captions at all — this isn't fixable by retrying, only an audio-transcription fallback would help, which this skill doesn't have).
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

The script exits 1 and prints `{"error": "..."}` on failure rather than a stack trace — read that message directly instead of guessing:

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page. Retrying with different `--language` values will not help this case.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **"No transcript found. Try specifying a language..."**: this means the default (no-`--language`) call couldn't resolve a track — **add** an explicit `--language` list guessed from the video's apparent language (see Workflow step 2). This is the opposite fix from "wrong language was specified."
- **A specified `--language` came back empty**: drop `--language` (or broaden the list) to fetch whatever's available, then tell the user the actual language returned.
- **Dependency missing**: run the Setup command above and retry.

## Known Limitations

- Only works for videos that have captions available (manual or auto-generated) — there's no audio transcription fallback. If YouTube shows no captions in the player, this script can't produce one either.
- This skill only covers on-demand single-video processing. A recurring "fetch new videos from these channels daily" pipeline is a separate, larger build (tracking manifests, backfill ordering, dedup state) and isn't included here.

## File Structure

```
SKILL.md
scripts/
  fetch_transcript.py   Fetches transcript via youtube-transcript-api, JSON or plain text out (stdlib + 1 dependency)
reference/
  output-formats.md     Worked examples for each output format
```
