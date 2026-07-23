# Briefing template

The shape of the generated `<project>-product/SKILL.md`. Drop any section with nothing true to say in it; an empty heading teaches the next agent that the section is decorative.

## Frontmatter

```yaml
---
name: <project>-product
description: >-
  Product briefing for <App> — <what it is, one clause>. Read BEFORE
  implementing a feature, fixing a bug, or answering any question about how
  or why <App> behaves. Covers <domain vocabulary, comma-separated>.
---
```

The description carries the load path, so it earns both halves. The broad clause fires on requests that name no feature — *"add a setting for this"*, *"fix this crash"* — which are the requests that need the briefing most. The vocabulary list fires on the app's own words, harvested from user-facing strings and the user's phrasing during the grilling. Over-triggering costs one file read; under-triggering costs the whole briefing.

## Body

````markdown
> Generated <date> at <short sha>. The code is ground truth: where it
> contradicts this briefing, follow the code and say so out loud, so this
> gets fixed.

## What this is

Two or three lines: what the product does, for whom, and what a user is
trying to accomplish when they open it.

## Load-bearing

The flow the product exists to deliver, and what must never regress.
Rank the rest as secondary so the next agent knows what it is touching.

- **<Flow name>** — <why it is the core>. `path/to/Entry.kt:40`
- Secondary: <feature>, <feature>.

## Invariants

Rules that must hold, each with the bug that proved it. The bug is the
part that makes the rule stick.

- **<Rule stated as an always/never>** — <consequence when broken>.
  `path/to/Rule.kt:88`
  Learned from: <what broke, and what the user saw>.

## Entitlements

Tiers, roles, flags, and plan gates — and every exception. Exceptions carry
the most history per line, so give each its reason.

- **<Feature>** — <who gets it>. `path/to/Gate.kt:31`
  Exception: <who is grandfathered or excluded, and why>.

## Flows

Each key flow as the user experiences it, in their words, anchored to where
it lives in code.

### <Flow name>
1. <user-visible step> — `path/to/Screen.kt:120`
2. <user-visible step> — `path/to/Handler.kt:64`

Rules that only apply here: <rule>.

## Runbook

How to run the app and reach each flow, so a change can be watched rather
than assumed.

```bash
<run command>
```

- **<Flow>** — <route, deep link, tap path, or CLI invocation>.
  Needs: <seed data, account state, permission, or device condition>.

## Landmines

Places that look safe and are not.

- **<Area>** — <what goes wrong and why it is not visible from the code>.
  `path/to/Trap.kt:12`

## Open questions

Unresolved after the grilling. Recorded as unknown rather than guessed, so
no agent treats a guess as settled.

- <question>
````
