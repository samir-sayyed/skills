---
name: onboard-agent
description: Build a product briefing skill for this repo, by analysing the code and grilling you about what the code cannot say.
disable-model-invocation: true
---

Coding agents write wrong code on a healthy codebase for four reasons the source cannot fix. They break an **invariant** nobody wrote down. They miss the exception buried in an **entitlement**. They refactor a **load-bearing** flow as though it were decoration. They ship without a **runbook**, so they never watch their own change behave.

All four failures share a cause: the knowledge is **tacit** — alive in the user's head, absent from the repo.

This skill extracts that tacit knowledge into a **briefing**: a project-specific skill that loads for every future agent on this repo.

Works on any stack. Android, iOS, frontend, backend, CLI.

## Branches

- **Generate** — no arguments, or a repo path. Run every step.
- **Deepen** — arguments name a wrong belief or one area (*"the agent keeps getting the trial wrong"*, *"deepen the calendar flow"*). Read the existing briefing, then run steps 4–7 scoped to that section alone.

## 1. Detect the stack

Identify each stack in the repo from its marker files, then read that row of [Where product signal hides](#where-product-signal-hides). A monorepo has several rows; take them all.

**Done when:** every stack in the repo is named, and you can state the command that runs the app.

## 2. Harvest existing docs as claims

Read `README`, `CLAUDE.md`, `AGENT.md`, `AGENTS.md`, `docs/`, ADRs, and recent commit messages.

Every statement you find is a **claim to verify**, never a fact. Check each against current source. A claim the code confirms becomes a high-confidence strawman item. A claim the code contradicts becomes a finding to raise with the user — those contradictions are often the exact belief the agent has been acting on.

**Done when:** every product claim in existing docs is marked confirmed, contradicted, or unverifiable.

## 3. Analyse along the four axes

Read source for what the four failure modes need. The signal lives in different places per stack, but the axes never change:

- **Load-bearing** — which flow the product exists to deliver. Entry points, launcher/root routes, the screen or endpoint everything else returns to, the paths with the most defensive code around them.
- **Invariants** — relationships that must hold. Look in validation, assertions, migrations, and bug-fix commits: a fix with no test is usually an invariant someone learned the hard way.
- **Entitlements** — tier gates, roles, feature flags, plan checks, and their exceptions. Grandfathering clauses and legacy-user branches carry the most tacit history per line.
- **Runbook** — how a human reaches each flow: run command, route, deep link, tap path, CLI invocation, seed data or state needed to trigger it.

**Done when:** each axis holds at least one concrete, file-anchored statement, and every statement you are unsure of is marked low-confidence.

## 4. Build the strawman

Compose what you inferred as flat assertions, grouped by axis, each carrying its **anchor** — the `path/to/file.ext:line` it came from — and a confidence marking.

Assert; do not hedge. *"Focus Sessions is the load-bearing feature; schedules are secondary"* earns a sharp correction. *"What is your core feature?"* earns a vague paragraph. A wrong strawman item is the most valuable thing you can produce here — it exposes the belief the agent has been coding against.

**Done when:** every axis has a strawman the user can answer with yes, no, or a correction.

## 5. Grill

Put the strawman to the user one item at a time, waiting for feedback on each. Asking multiple questions at once is bewildering.

For each, provide your recommended answer.

If a *fact* can be found by exploring the environment, look it up rather than asking. The *decisions* are the user's — put each one to them and wait.

Work axis by axis, low-confidence items first. Follow a correction wherever it leads before moving on: a corrected invariant usually has a bug behind it, and that bug is the reason the invariant exists. Ask for it.

Watch the answers. While they stay rich, keep going. When they shorten to a word, close the axis, record what is still unsettled as an open question, and move on.

**Done when:** every strawman item is confirmed, corrected, or recorded as an open question — none silently kept.

## 6. Write the briefing

Write `<repo>/.claude/skills/<project>-product/SKILL.md`, following [`TEMPLATE.md`](TEMPLATE.md).

Name it for the project: `quiet-hours-product`, `acme-api-product`.

Every line earns its place by being something the code cannot say. Module maps, class lists, and data models are already in the source and rot the day after generation; the briefing holds the why, the rule, the exception, and the path to reach it.

Before writing a claim, read the code at its anchor. A well-commented codebase already carries the *why* at the site, and repeating it pays context to say nothing. What the comment cannot carry is what survives: the production consequence (*what users saw when this broke*), the instruction not to change it (*these two branches look like duplication; leave them apart*), and the judgement that the code has no room for (*this is deliberate, do not harden it*).

**Done when:** every claim carries an anchor, every axis has a section, and no claim restates a comment already sitting at its anchor.

## 7. Wire the load path

A briefing nothing loads is the problem you started with.

Put a two-line pointer at the **top** of `CLAUDE.md`, or `AGENTS.md` where the repo uses that — the first thing in the file, above any existing content. Agents orient by reading the start of these files, and a long one gets truncated before its end; a pointer appended at the bottom is the same unread footnote you set out to fix.

Place it **outside** any tool-owned block — markers like `<!-- cce-block -->` get rewritten and will swallow anything inside them. A block that starts at line 1 is prepended to, not appended after.

```markdown
## Product context
Read `.claude/skills/<project>-product/SKILL.md` before implementing a feature, fixing a bug, or answering how or why this product behaves.
```

Then report to the user: the path written, the contradictions found in step 2, and the open questions left.

**Done when:** the pointer is in a file the agent loads on its own, and it sits outside every tool-owned block.

## Where product signal hides

| Stack | Markers | Read for product signal |
|---|---|---|
| Android | `AndroidManifest.xml`, `build.gradle` | manifest components and intent filters, billing SKUs and entitlement checks, `strings.xml`, Room migrations, Alarm/WorkManager scheduling |
| iOS | `Info.plist`, `*.xcodeproj`, `Package.swift` | `Info.plist` capabilities, StoreKit products, `Localizable.strings`, CoreData model versions, background modes |
| Web frontend | `package.json` plus a router | route table, i18n catalogs, feature flags, analytics event names, auth guards and redirects |
| Backend | OpenAPI spec, route files, `migrations/` | endpoint surface with authz middleware, migrations, background jobs, webhooks, plan and tier tables |
| CLI or library | `bin/`, package exports | command surface and flags, public API exports, README examples |
| Unknown | — | entry points, config schema, user-facing strings, test names, migration history |

User-facing strings and test names are the highest-yield product signal on every stack: both are written in the language of the user, not of the code.
