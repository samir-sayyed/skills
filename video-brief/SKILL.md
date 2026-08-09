---
name: video-brief
description: Turn a YouTube video into a short HTML learning brief — the actual takeaways plus how to apply them to coding, AI work, and personal life — so a 20–30 minute video becomes a 4 minute read. Pulls the transcript from YouTube captions with yt-dlp, then publishes the brief as an Artifact. Trigger on "brief this video", "video brief", "summarize this talk", "what should I take from this video", "/video-brief <url>", or any bare YouTube URL sent with an ask to learn from it rather than watch it.
---

# Video Brief

One video in, one published HTML brief out. No quiz, no Q&A — learnings and application only.

## Inputs

A YouTube URL. Several URLs = several briefs, one per video, run the pipeline once per URL.

**Queue mode** — when invoked with no URL, or asked to "process the queue", read `~/video-queue.txt`. Ignore blank lines and `#` comments; every remaining line is a URL. Run the pipeline once per URL, then move each finished line into `~/video-queue.done.txt` in the form:

```
2026-07-24  https://youtu.be/…  →  https://claude.ai/code/artifact/…
```

Leave a line in the queue if its brief failed, and say which and why at the end. An empty queue means exit without output — no brief, no summary, no "nothing to do" artifact. This is what the 06:57 launchd job runs, so silence on an empty queue matters.

## Pipeline

Everything below is deterministic. Run it, don't redesign it.

### 1. Pull the transcript

```bash
~/.claude/skills/video-brief/transcript.sh "<YOUTUBE_URL>" <SCRATCHPAD>/transcript.txt
```

Takes a few seconds. First line of the output file is the real video title — use that, not the URL slug. No auth, no API key.

Read the transcript file in full.

Transcripts arrive with no punctuation and mangled proper nouns ("DSPI" for DSPy, "Jeepa" for GEPA, "fi code" for VS Code). Correct them silently in the brief.

Exits non-zero with `no captions` when the video has none. Say so plainly and stop — don't guess from the title, and don't download the video to transcribe it yourself.

### 2. Write the brief

Copy `template.html` from this skill directory to the scratchpad, then fill every `REPLACE`. The template carries the visual identity — **do not redesign it**, so consecutive days look like a series. Delete any section with no real content rather than padding it.

Content rules:

- **Learnings are claims, not topics.** "Constraints belong in code, not in the prompt" — not "The role of constraints".
- **4–7 learnings.** Most useful first. If the video only had two real ideas, write two and say the rest was filler in the Skipped section.
- **Apply it is the point of the whole page.** Three lanes: day-to-day coding, AI work, personal. Every bullet starts with a verb and names something concrete — a real habit, tool, or file. Vague advice ("consider adopting this mindset") is a failure.
- **An empty lane is an honest answer.** A video about distributed systems has nothing for the personal lane. Say "Nothing here — this one is purely technical" rather than manufacturing a bullet.
- **Everything traces to the transcript.** Don't import outside knowledge about the topic. If the speaker's claim is contested, the colophon already notes claims are theirs.
- **Cut the video's throat-clearing.** Applause, thanks, plugs, and "check out our Discord" never make the brief.

### 3. Publish and keep

Save the finished HTML to `~/video-briefs/YYYY-MM-DD-slug.html` before publishing — the scratchpad is session-scoped and gets wiped, so that folder is the only durable copy of the file itself.

Then queue it for the second brain (see `~/brain/AGENTS.md`) by stripping the HTML to text:

```bash
~/brain/queue-brief.sh ~/video-briefs/YYYY-MM-DD-slug.html
```

This drops the text into `~/brain/raw/`. Step 4 turns it into wiki pages.

```
Artifact(file_path=<the filled html>, favicon="📺",
         description="<one line: what the video argues>")
```

### 4. Ingest into the brain

Follow the **Ingest** section of `~/brain/AGENTS.md` — that's the procedure, don't restate
or redesign it here. Read the transcript you already have rather than re-reading `raw/`.

Four things this pipeline gets wrong if left unsaid:

- **Enrich before you create.** Read the existing concept pages an idea touches. A claim
  that restates a page you already have belongs *in* that page, not beside it. Ingests that
  only add files are under-processed.
- **Never write unverified claims onto `wiki/projects/`.** The brief's "apply it" lanes are
  recommendations about Samir's repos, not facts pulled from the clone. Project pages take
  facts only.
- **Say what you didn't do.** The `log.md` entry names what was enriched vs created and what
  you deliberately left alone. That entry is the review surface.
- **Mark unattended runs.** If this ran from the 06:57 launchd job, tag the log entry
  `(unattended)` so it's obvious which synthesis nobody watched.

Then run `bash ~/brain/audit.sh` and fix anything it flags before reporting done.

Nothing here commits — the wiki changes sit as an uncommitted diff in `~/brain` until Samir
reviews them. `git -C ~/brain diff` is the undo button. Do not commit it for him.

### 5. Report

Give the user the URL, one line on what the video was, and the single most applicable action from the brief. Then one line naming the wiki pages created and enriched. Nothing else — the page is the deliverable.

## Notes

- Requires `yt-dlp` on PATH (`brew install yt-dlp`). Nothing else — no login, no API key, no session that expires mid-run.
- Runtime is dominated by writing the brief and the brain ingest. The transcript itself takes seconds.
- Cross-video questions live in `~/brain`, not in a transcript store. Don't rebuild a video corpus here.
