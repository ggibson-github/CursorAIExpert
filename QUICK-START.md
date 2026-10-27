# Quick Start Guide

## What This Is

An expert system that turns a specification into design docs, diagrams, tasks, code, and tests. All work happens inside a Work Item (`WID-…`). The expert journal and that Work Item's active branch are the source of truth across sessions.

This folder is the Cursor expert. Workflow rules are in `AGENTS.md`. Skills are Cursor Agent Skills in `.cursor/skills/<name>/SKILL.md`. Hooks in `.cursor/hooks.json` load the journal and the rules that match the action about to run. Fixed choices use the AskQuestion tool.

Journal hooks run with `py -3`. Note-merge hooks run with `bash` (Git Bash on PATH).

## Structure

```
D:\CursorAIExpert\
|-- AGENTS.md                         Workflow rules
|-- MyRole.txt                        Role and pipeline definitions
|-- QUICK-START.md
|-- docs\
|   `-- spec-to-artifacts-agent-skills-system.md
|-- facts\
|   |-- MEMORY-INDEX.md               Expert memory navigation
|   `-- HOW-MEMORY-LOADING-WORKS.md
|-- scripts\
|   |-- memory\build_trigger_index.py Rebuilds the action-trigger index
|   |-- test_journal_hook.py
|   `-- test_rules_hook.py
|-- work-items\_TEMPLATE\             Copied when a Work Item is created
|-- qa-sessions\_TEMPLATE\            Copied when an operator Q&A session is created
`-- .cursor\
    |-- hooks.json                    Cursor hook events
    |-- CONTEXT-SYSTEM.md             Active Work Item pointer
    |-- active-context.txt            work-item:WID-...
    |-- workflows\
    |   |-- workflow-registry.json    developer pipeline
    |   |-- developer.md              Phase sequence and gates
    |   `-- README.md
    |-- hooks\
    |   |-- inject_journal_context.py Journal text for the turn and each tool
    |   |-- inject_rules_on_action.py Rules for the action about to run
    |   |-- merge-agent-notes.sh
    |   |-- post-journal-update.sh
    |   |-- on-stop.sh
    |   `-- on-subagent-stop.sh
    `-- skills\
        |-- define-role\SKILL.md      Define the developer role before work items
        |-- continue\SKILL.md         Resume from the journal
        |-- workflow-selector\SKILL.md Choose a pipeline for a new Work Item
        |-- switch-context\SKILL.md   Change the active Work Item
        |-- spec-parser\SKILL.md      Parse a spec and raise blocking questions
        |-- diagram-generator\SKILL.md Rebuild diagrams from HLD/DD
        |-- scaffold-project\SKILL.md Create the project skeleton
        |-- implement-feature\SKILL.md Implement one TODOS task
        |-- iterative-feature\SKILL.md Add or change a feature
        |-- refactor\SKILL.md         Reduce duplication and tech debt
        |-- journal-keeper\SKILL.md   Update the journal after a phase
        |-- remember\SKILL.md         Capture a fact or rule
        |-- operator-qa\SKILL.md      Journaled Q&A (AskQuestion and chat)
        |-- integrate-docs\SKILL.md   Fold docs into facts, rules, and MyRole.txt
        |-- promote-facts-rules\SKILL.md Elevate Work Item learnings
        |-- memory-optimize\SKILL.md  Check expert-memory health
        `-- visual-page\SKILL.md      Shared visual page beside chat
```


## Operator Q&A

Use **operator-qa** when clarifying requirements, building a spec with the user, verifying assumptions before work, or verifying notes before remember. Sessions live under `qa-sessions/`, keep a journal of questions and answers, and close into `conclusions.md`. Prefer AskQuestion for fixed choices; use chat for open-ended answers. The agent may start a session on its own when a human answer would change the plan.


A new Work Item starts from the template (journal, status, task list, and facts). Design docs, diagrams, and tests are added as the pipeline runs.

```
work-items\<WID>\
â”œâ”€â”€ journal\progress.md                    # Session state for this Work Item
â”œâ”€â”€ STATUS.md
â”œâ”€â”€ TODOS.md
â”œâ”€â”€ spec.md                                # Optional; or a path you provide
â”œâ”€â”€ facts\
â”‚   â”œâ”€â”€ facts.md                           # Work Item facts
â”‚   â””â”€â”€ rules.md                           # Work Item rules
â”œâ”€â”€ docs\
â”‚   â”œâ”€â”€ design\                            # requirements-summary.md, hld.md, dd.md
â”‚   â”œâ”€â”€ diagrams\                          # *.mmd and index.html
â”‚   â””â”€â”€ features\<feature-id>\             # Iterative feature spec, design, approval
â””â”€â”€ tests\                                 # When this Work Item owns its tests
```

Active context is `.cursor\active-context.txt`, formatted `work-item:WID-â€¦`. `.cursor\active-work-item.txt` is the legacy pointer.

## Getting Started

### 1. Start or resume

Open this folder and say **"start"**, **"continue"**, or **"resume"**.

The continue skill will:

1. Read `MyRole.txt`. If `Role status` is `pending`, run **define-role** and stop. It asks for the specific job, which workflows and skills apply, and any notes you already have (standards, architecture notes, runbooks, setup notes). "I have no notes" is a real answer. "Continue" does not answer those questions.
2. After "I approve the role" or "Skip role definition", read `.cursor\active-context.txt` (or the legacy active-work-item file).
3. If nothing is active, ask for a Work Item ID such as `WID-21411151`.
4. Create `work-items\<WID>\` from `work-items\_TEMPLATE\` when that folder does not exist.
5. If the journal has no workflow type, run **workflow-selector**. It reads `MyRole.txt` and offers only workflows still listed in `workflow-registry.json`.
6. Perform the single next action recorded in `work-items\<WID>\journal\progress.md`.

To change Work Items later, say **"switch to work item WID-â€¦"**.

### 2. The developer pipeline

From `.cursor\workflows\developer.md`:

`spec-parser â†’ hld-writer â†’ dd-writer â†’ diagram-generator â†’ task-breakdown â†’ git-workflow (setup) â†’ scaffold-project â†’ implement-feature (loop) â†’ test â†’ git-workflow (commit/PR) â†’ done`

**Iterative feature** (say "add a new feature" or "change an existing feature"): requirements â†’ design â†’ approval â†’ branch â†’ implement â†’ test â†’ commit/PR.

HLD, DD, task breakdown, and git steps are phases in the developer workflow. They do not have their own skill folders. **diagram-generator**, **scaffold-project**, and **implement-feature** do.

### 3. Human gates

The pipeline pauses until you approve:

- **HLD and its diagrams** â€” "I approve the HLD" or "Skip HLD approval"
- **DD and its diagrams** â€” "I approve the DD" or "Skip DD approval"
- **Feature design** (iterative work) â€” "I approve the feature design" or an explicit waiver

"Continue" is not approval and not an answer to an open question. If the next action is a wait, continue only re-prompts.

### 4. What you can say

| What you say | What happens |
| --- | --- |
| "start" / "continue" / "resume" | Define the role if it is pending; otherwise read the journal and perform the next step |
| "define my role" | Run role onboarding, including any notes you already have |
| "I approve the role" | Save the role, workflows, and skills and allow Work Items |
| "switch to work item WID-â€¦" | Point later steps at that Work Item |
| "I approve the HLD" | Clear the HLD gate and move to DD |
| "I approve the DD" | Clear the DD gate and move toward scaffold and implementation |
| "Skip HLD approval" | Waive that gate |
| "remember this â€¦" | Store a fact or rule on the Work Item, or in Expert Role memory |
| "integrate this â€¦" | Fold a document into facts, rules, and `MyRole.txt` |
| "promote facts/rules" | Review Work Item learnings for Expert Role memory |
| "add a new feature" | Start the iterative-feature workflow |
| "refactor" | Reduce tech debt and keep tests passing |

"Remember this" does not write `docs\facts\captured.md`. Work Item captures go to `work-items\<WID>\facts\`. Expert Role captures go to the workflow memory files under `facts\`, with a pointer in `facts\MEMORY-INDEX.md` when the topic is new.

### 5. Journal

`work-items\<WID>\journal\progress.md` tracks:

- Workflow type and current phase
- Next action
- Open questions (blocking and deferred)
- Resolved Q&A
- Blockers
- Artifacts

### 6. Templates and HLD depth

Before HLD or DD, the system asks whether you have a template to follow.

HLD profiles:

- **Standard** â€” context and architecture
- **Part 1** â€” Extended through Dependencies
- **Extended** â€” full document, including non-functional requirements and compliance

### 7. What the pipeline produces

- Mermaid diagrams (architecture, sequence, ER, C4-style) and `docs\diagrams\index.html`
- Design docs under `work-items\<WID>\docs\design\`
- `TODOS.md`, including environment setup before package installs
- Unit and integration tests
- A feature branch `feature\WID-<id>` and, when you ask, a commit and pull request

Tests must pass before a push.

### 8. Safety

The system will:

- Ask blocking questions before moving past spec
- Ask about dependencies, downloads, and credentials instead of skipping them
- Refactor when a change would duplicate logic
- Run tests before push
- Install the environment the design calls for, before libraries

The system will not:

- Skip a phase the journal still has open
- Treat "continue" as approval
- Push while tests are failing
- Assume a workaround for a blocker

## Example

```
You: start
Agent: What are you working on? (work item WID-XXXXXXXX)
You: WID-21411151
Agent: [creates work-items\WID-21411151\ from the template]
       [asks you to select the developer pipeline]
       [reads work-items\WID-21411151\spec.md, or asks where the spec is]

       I have 3 blocking questions:
       1. What database should we use?
       2. Do you need authentication?
       3. Should this support multiple tenants?
You: 1. PostgreSQL, 2. Yes - OAuth2, 3. No, single tenant
Agent: [records the answers in Resolved Q&A]
       [sets next action to "run hld-writer"]

       Do you have an HLD template I should follow?
You: No, use Standard profile
Agent: [writes work-items\WID-21411151\docs\design\hld.md]
       [writes diagrams and updates docs\diagrams\index.html]
       [sets next action to "wait for HLD approval"]

       HLD is ready. Reply "I approve the HLD" to proceed.
You: I approve the HLD
Agent: [records approval and sets next action to "run dd-writer"]
```

## Troubleshooting

- **Continue is not advancing.** Read **Next action** in the Work Item journal. A wait for approval or an open blocking question needs a real answer, not another "continue".
- **A dependency or download failed.** The agent will stop and ask for a URL, credential, or other help. Answer before it proceeds.
- **You want a different next step.** Edit **Next action** in `work-items\<WID>\journal\progress.md`, then say "continue".

## Learn more

- `AGENTS.md` â€” workflow rules
- `.cursor\CONTEXT-SYSTEM.md` â€” how the active Work Item is stored
- `.cursor\workflows\developer.md` â€” phase sequence, gates, and artifact paths
- `facts\MEMORY-INDEX.md` â€” how expert memory is organized
- `docs\spec-to-artifacts-agent-skills-system.md` â€” longer description of the system
