---
name: diary-memory
description: Keeps a compact persistent memory across sessions by saving one-line notes to an append-only diary and folding older notes into hierarchical summaries. Use when the user says remember this, what did we decide last time, or catch me up on this project. Use when working on multi-session projects where the agent needs to recall prior decisions and context without bloating the prompt. Do not use for storing secrets, passwords, API keys, or personal data. Do not use for editing past notes, storing full conversations, or replacing project documentation.
license: MIT
---

# Diary Memory

Keeps a persistent, logarithmic-size project memory across sessions using append-only notes and power-of-two folded summaries.

For internal file schemas and folding math, see [how-it-works.md](references/how-it-works.md).
Helper CLI implementation is located at [memory.py](scripts/memory.py).

## When to Use

Activate this skill when:
- The user asks to remember a decision, requirement, or milestone (e.g. "remember this", "note that we decided on SQLite").
- Starting a new session or resuming work (e.g. "what did we decide last time", "catch me up on this project").
- Searching for past architectural choices or debugging conclusions across long project histories.

## First-Time Setup: What to Gather

Before recording notes on a new project, verify two setup choices:
1. **Diary Location**: Confirm whether `.diary/` in the project root is acceptable or if a custom path should be set via `DIARY_DIR`.
2. **Sharing Preference**: Ask whether the diary should be shared with the team via Git (tracked) or kept private to this machine (added to `.gitignore`).

## Step-by-Step Workflow

### 1. Resuming a Session (`wake`)
Run `wake` at session start to restore context:
```bash
python scripts/memory.py wake
```
- Reads the newest 8 notes in full and displays older notes as folded block summaries.
- If the output includes `SUMMARY NEEDED for block [lo-hi)`, immediately run the `nap` workflow before proceeding.
- Produce a **2 to 4 line "where we left off" recap** for the user. Never paste the entire raw diary unless explicitly asked.

### 2. Saving a Decision or Note (`note`)
When a milestone, decision, or user instruction should be preserved:
```bash
python scripts/memory.py note "<one-line note text>"
```
- Notes must be concise (max 300 chars) and contain no credentials or sensitive tokens.
- Return a **one-line confirmation** to the user (e.g. `Saved note #4: Switched auth from JWT to sessions.`).
- If the command outputs `SUMMARY NEEDED for block [lo-hi)`, proceed to step 3.

### 3. Folding Summaries (`nap`)
When a command reports a summary is needed:
```bash
python scripts/memory.py nap
```
- Review the 2 child items (either 2 raw notes or 2 child block summaries).
- Synthesize the essential information into a single one-line summary (max 240 chars).
- Save the summary:
```bash
python scripts/memory.py nap <LO> <HI> "<synthesized summary>"
```
- Repeat if another summary is needed until all eligible older blocks are consolidated.

### 4. Searching Past Notes (`recall`)
Search past raw notes with a case-insensitive regex or keyword:
```bash
python scripts/memory.py recall "<pattern>"
```
- Returns up to 20 matching notes with IDs and dates.

### 5. Inspecting Specific Ranges (`zoom`)
To inspect original raw notes summarized inside an older block:
```bash
python scripts/memory.py zoom <LO> <HI>
```

## Agent Output Formatting

- **After `wake`**: Provide a crisp 2 to 4 line summary highlighting:
  1. Primary architectural/technical decisions made previously.
  2. The most recent task completed.
  3. The immediate next priority.
- **After `note`**: Provide a single line confirmation.
- **Guardrail**: Never dump the raw diary contents unless the user explicitly requests full raw logs.

## Strict Rules and Prohibitions

- **NO Secrets**: Never store passwords, API keys, bearer tokens, or personal identifiers.
- **NO History Editing**: Never manually edit or delete lines in `LOG.txt`. Notes are append-only.
- **NO Hallucinations**: Never invent memories or fill gaps with unconfirmed assumptions.
- **NO Conversation Dumps**: Do not store verbatim chat transcripts. Record only high-level decisions and outcomes.
- **NO Documentation Replacement**: Diary memory tracks session progress and decisions, not user manuals or API specs.
