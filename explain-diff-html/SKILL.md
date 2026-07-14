---
name: explain-diff-html
description: Use when the user asks for a rich explanation of a code change, diff, branch, or PR. Produces a self-contained interactive HTML page with background, intuition, code walkthrough, and a quiz.
---

# Explain Diff

> Originally based on [Explain Diff](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524) by [Geoffrey Litt](https://github.com/geoffreylitt), adapted here with a fixed quiz format (deterministic randomized option order, equal-length options) and a few other refinements.

Please make me a rich, interactive explanation of the specified code change.

It should have these sections:

- Background: Explain the existing system relevant to this change. (You should broadly explore surrounding code for this.) We don't know how much the reader already knows, so include a deep background for beginners (note that it can be skipped if the reader is already familiar), and then a more narrow background directly relevant to the change.
- Intuition: Explain the core intuition for the code change. The focus here is to explain the essence, not the full details. Use concrete examples with toy data. Use figures and diagrams liberally.
- Code: Do a high-level walkthrough of the changes to the code. Group/order the changes in an understandable way.
- Quiz: Come up with five questions that test the reader's knowledge of this PR. This should be medium difficulty, difficult enough that you actually need to understand the substance of the PR to answer them, but not gotchas. The goal is to help the reader make sure that they've actually understood. These should be presented as interactive multiple-choice questions, and when the user clicks, it tells them whether they were correct and gives feedback.

## Quiz quality rules (important — the quiz is useless if the answer is guessable)

The correct answer must not be identifiable without reading the question. Enforce all of these:

1. **Equal-length options.** All options for a question must be of similar length (within roughly ±20% of each other in character count). Never make the correct answer the longest or most detailed one. If the correct answer needs detail, pad the distractors to match; if the distractors are short, shorten the correct answer.
2. **Deterministic randomized positioning.** Do not hand-place correct answers (they otherwise cluster on option B). Store each question's options in the JavaScript data with the correct answer first, then shuffle option order at render time with a seeded (deterministic) shuffle — e.g. seed a tiny PRNG (mulberry32 or similar) with a hash of the question text, and Fisher–Yates shuffle the options with it. Same file → same order every load, but positions are uniformly distributed across questions. Track the correct answer by identity, not by index.
3. **Plausible distractors.** Every wrong option must be something a reader who skimmed the PR might genuinely believe — e.g. describing the old behavior, a related-but-different mechanism, or a common misconception. No obviously-silly throwaway options.
4. **Uniform specificity and tone.** Distractors must use the same level of technical specificity as the correct answer (same kind of nouns, same hedging). Avoid tells like absolutes ("always", "never") only in wrong answers or precise numbers only in the right one.
5. **Feedback teaches.** On answer, show whether it was correct, and in both cases explain *why* the correct answer is correct and why the chosen distractor is wrong. Let the reader retry other questions; show a score summary at the end.
6. **Self-check before saving.** Scan the finished quiz data and verify: (a) no correct answer is the longest option in its question, (b) correct answers land on at least three different positions across the five questions after the seeded shuffle, (c) every distractor passes the "could a skimmer believe this?" test. Fix violations before writing the file.

## Format

- Output a single self-contained HTML file which includes CSS and JavaScript — no external resources (no CDN scripts, fonts, or images), so it works offline. Make the whole thing one long page with section headers and a sticky/linked table of contents. Don't use tabs for the top-level structure. Basic responsive styling so you can view it on a phone is nice too.
- Put the file in a global place on my computer outside of the code repo, and make sure the filename always starts with today's date in `YYYY-MM-DD-` format, because it helps keep the files time-sorted and out of version control. For example: `/tmp/2026-01-12-explanation-<slug>.html`. After saving, print the absolute path so I can open it.
- Please write with the clarity and flow of Martin Kleppmann, making it engaging and written in classic style. Transitions between sections should be smooth.
- Some tips on diagrams. Ideally, you should pick a small number of diagram families that can be reused throughout the explanation to explain various cases. Some useful kinds of diagrams:
  - A very simplified version of the UI that the user sees in the app, to explain UI changes.
  - A system diagram showing data flow or communication between components. Make sure to include example data here!
  - A before/after pair using the same diagram family, so the reader can spot exactly what the change altered.
- Don't use ASCII diagrams. Always use simple HTML/CSS designs for your diagrams, HTML lists for lists of things, etc. Inline SVG is fine for anything CSS boxes can't express.
- For code blocks, always use `<pre>` tags. If you use a custom styled div instead, it **must** have `white-space: pre-wrap` in its CSS, or the browser will collapse all newlines into a single line. Before saving the file, scan each code block in the HTML source and confirm its CSS includes `white-space: pre` or `pre-wrap`.
- Use callouts for key concepts or definitions, important edge cases, etc.
- Support dark mode via `@media (prefers-color-scheme: dark)` — at minimum, background, text, code blocks, and callouts must stay readable in both schemes.
