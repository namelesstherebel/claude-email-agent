# RUNTIME.md — Self-Improving Runtime

> Version: 1.0.0
> This file is installed and managed by the agent-onboarding runtime.
> Do not delete it — the agent uses it to track friction and improve.

---

## What This Is

The self-improving runtime monitors agent tasks for friction — gaps in specs, missing context, unclear intent, backtracking — and generates improvement proposals into `IMPROVEMENT_QUEUE.md`.

Proposals are reviewed by the user via `*review`. Nothing changes in the repo until you approve.

---

## Runtime Behavior

After every task in this repo, the agent will:

1. Review what happened during the task
2. Identify any friction points (missing info, wrong assumptions, repeated corrections)
3. Generate 0-3 improvement proposals if friction was detected
4. Output a completion notice:

**If proposals were generated:**
```
Task complete. Review queue has N pending proposal(s). Run *review to approve, reject, or modify.
```

**If no proposals:**
```
Task complete. Improvement queue is clean. No proposals pending.
```

---

## Friction Signals Tracked

| Signal | Example |
|---|---|
| Missing spec | Agent had to guess how filtering works |
| Outdated context | System prompt didn't mention recent policy change |
| Repeated correction | User corrected the same thing twice |
| Unclear intent | Trade-off rule was ambiguous |
| Scope creep | Task required undocumented capability |

---

## Commands

| Command | What it does |
|---|---|
| `*review` | Surface pending proposals for approval/rejection |
| `*reflect` | Manually trigger a friction review |
| `*status` | Report spec coverage, queue depth, last activity |

---

## Approval Process

For each proposal, the agent shows:
- What triggered it
- Which file it proposes to change
- The exact change written out
- A confidence level (high/medium/low)

Respond with `APPROVE`, `REJECT`, or `MODIFY`. Nothing changes until you do.
