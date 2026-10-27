---
name: operator-qa
description: >-
  Runs a self-contained question-and-answer session with the human operator to
  clarify conversation, build specs, verify assumptions before work, or verify
  notes before persisting them. Creates a qa-sessions folder with a journal,
  records Q&A turns, then extracts answers into conclusions for next steps.
  Use when clarifying requirements, checking assumptions, confirming notes,
  building a spec with the operator, helping create a new project spec, or when
  the operator says start a Q&A session, clarify with me, verify this, or ask me
  questions.
disable-model-invocation: false
---

# Operator Q&A

## Purpose

Hold a focused Q&A session with the human operator. Keep all turns in a session journal. When the session ends, extract answers into conclusions that drive the next action (spec text, work plan, verified notes, assumption list, or pipeline updates).

## Work item branch

Keep the question transcript in this session journal. Present a fixed choice with **AskQuestion**. Ask an open-ended question in chat. When a question blocks the current work item, also add a node on that work item's map. The node id is unique and is not `work-item` or a phase name. Store the session id on the node and make it the active leaf through journal-keeper. When the session closes, store the decision and run the journal-keeper answer transition so `active` leaves this question. Do not copy every question onto the node. A decision for the whole work item or the expert goes in that flat journal.

## Session location

This expert is a single role. Sessions live at the expert root under `qa-sessions/`, same idea as `work-items/`.

Active session id file: `.cursor/active-qa-session.txt`

Ids are `Q` plus a counter: `Q1`, `Q2`, …

## Folder layout

```
qa-sessions/
  _TEMPLATE/
    PURPOSE.md
    STATUS.md
    journal/progress.md
    conclusions.md
  Q1/
    PURPOSE.md
    STATUS.md
    journal/progress.md
    conclusions.md
```

Copy `_TEMPLATE/` to `qa-sessions/<id>/` when opening a session.

## When to use

- Clarify ambiguous conversation or requirements
- Build or refine a spec with the operator (including "help me create a spec for a new project")
- Verify assumptions before performing work
- Verify notes or facts/rules before persisting them (often before remember)
- Operator says: "ask me", "clarify", "Q&A", "verify this with me", "let's nail this down"

**Initiate on your own** when a human answer would change the plan. Prefer this skill over inventing missing requirements.

Do not use this skill for silent pipeline steps that already have a clear next action and no blocking ambiguity.

## Phases

### 1. Open

1. Choose the next free id (`Q1`, `Q2`, …) under `qa-sessions/` (skip `_TEMPLATE`).
2. Copy `qa-sessions/_TEMPLATE/` to `qa-sessions/<id>/`.
3. Write `.cursor/active-qa-session.txt` with that id.
4. Fill `PURPOSE.md`: goal, context (work item / topic / conversation), intended outcome (`spec` | `assumptions` | `notes` | `direction` | `other`).
5. Initialize `journal/progress.md` fields and set Next action to `ask`.
6. Tell the operator the session id and purpose in one short sentence, then present the first question(s) using the presentation rules below.

### 2. Ask

1. Ask only what is needed. Prefer one blocking question at a time. When several independent fixed-choice questions are ready, send them together in one AskQuestion call; otherwise walk through them one by one.
2. Present questions using **How to present questions** (AskQuestion vs chat). Do not rely on the model to invent AskQuestion on its own—follow those rules deliberately.
3. Append each asked question under **Open questions** in the journal with the date and presentation mode (`ask-question` or `chat`).
4. Set Next action to `wait for operator`.
5. Stop and wait. Do not invent answers. Do not continue the blocked work until answers arrive or the operator defers them.

## How to present questions

Choose the channel from the answer shape. Always journal the question either way.

### Use AskQuestion (choice UI)

Use the **AskQuestion** tool when it is available and the answer is a small fixed set:

- Yes / no / defer
- A short list of mutually exclusive options (at least two)
- Confirm / reject a proposed note, fact, rule, or assumption wording
- Pick among named alternatives (auth mode, scope in/out, priority, and similar)

When calling AskQuestion, pass a `questions` array. Each item has:

1. `id`: a short stable identifier, for example `auth-mode`.
2. `prompt`: the full question the operator sees.
3. `options`: at least two items, each with `id` and `label`.
4. `allow_multiple`: true only when several options may apply at once.

Do not add an "Other" option. Cursor adds one. Include an explicit defer option when postponing is valid, for example label `Defer for later`.

Prefer one blocking question at a time. When several independent fixed-choice questions are ready, send them in one AskQuestion call.

After the operator selects, treat the selected label as the answer and continue to Record.

If AskQuestion is unavailable, fall back to chat with the same options as a numbered list and ask the operator to reply with a number or label.

### Use chat (conversational)

Ask in the chat message when the answer is open-ended:

- Free-text requirements, acceptance criteria, or wording edits
- Explanations, examples, or "tell me how you want this to work"
- Anything that cannot be reduced to a short option list without losing meaning

In chat, ask one blocking question at a time unless the operator asked for a batch. Keep the question plain and specific.

### Mixed sessions

A single Q&A session may alternate: AskQuestion for closed choices, chat for free text. Record both the same way in the journal.

### 3. Record (when the operator replies)

In the same response as acknowledging the answer (from AskQuestion selection or chat text):

1. Move each answered item from Open questions to **Resolved Q&A** with date, question, answer, and presentation mode.
2. Note any deferred or refused questions under **Deferred**.
3. Update STATUS.md Last session summary.
4. Either ask the next question (phase Ask) or close (phase Close) when enough is known.

### 4. Close

1. Read the full journal Resolved Q&A and Deferred lists.
2. Write `conclusions.md` with:
   - **Session goal**
   - **Decisions / answers** (bullets tied to questions)
   - **Assumptions still open** (if any)
   - **Forward actions** (concrete next steps: write/update spec, create work item, run remember, proceed with pipeline phase, etc.)
   - **Artifacts to update** (paths)
3. Set journal Completion status to `done`, Next action to `done`.
4. Leave `.cursor/active-qa-session.txt` with the closed id for reference; next Open picks a new id.
5. Tell the operator the session is closed and point to `conclusions.md`.
6. Apply forward actions only after close, unless the operator asked to apply during the session.

## Journal fields

Keep these in `journal/progress.md`:

- Session ID, purpose
- Linked work item (if any)
- Outcome type: spec | assumptions | notes | direction | other
- Open questions
- Resolved Q&A (date, question, answer)
- Deferred
- Last completed, Next action
- Completion status
- Last session summary

## Rules

- One active Q&A session at a time unless the operator names another id to resume.
- To resume: set `.cursor/active-qa-session.txt` and continue from the journal Next action.
- Do not persist remember/facts/rules from unverified notes until this session closes with verification conclusions, when that was the purpose.
- Do not ask the operator to invent a session id; create it.
- Keep operator-facing questions plain and specific.
- Prefer AskQuestion for closed choices; do not present a fixed option set only as plain chat when AskQuestion is available.
- "Continue" is not an answer to an open Q&A question; wait for a substantive reply or AskQuestion selection.

## Examples

**Clarify before implement (closed choice, AskQuestion)**

1. Open Q3 with purpose "verify API auth assumption before implement".
2. Call AskQuestion with one question: id `auth-mode`, prompt "How should the API authenticate?", options `Bearer token required`, `Open on LAN`, and `Defer`.
3. Record the selected label, close the session, and write conclusions that say to update the design and proceed to implement.

**Help create a new project spec**

1. Open Q1 with outcome `spec`.
2. Ask in chat for goals, users, must-haves, out-of-scope items, and constraints. Use AskQuestion only for choices that have a short fixed set.
3. Close the session. Conclusions list the forward actions to write the spec and start a Work Item or run spec-parser.

**Verify notes before remember (yes/no via AskQuestion; edits in chat)**

1. Open Q4 with outcome `notes`.
2. Call AskQuestion: id `persist-rule`, prompt "Persist this as an expert-role rule?", options `Yes, store as written`, `Yes, but I will edit`, `No`, and `Defer`.
3. If the operator chooses edit, ask in chat for the revised wording.
4. Close the session. Conclusions say to run remember with the verified wording.
