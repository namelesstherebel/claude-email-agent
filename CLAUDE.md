# CLAUDE.md — Agent Context

> This file is automatically loaded by Claude Code.
> It provides the agent with full context about this project.

---

## Project

**claude-email-agent** — A self-improving Gmail auto-reply agent powered by Claude AI.

This is a template repo. When initialized, it creates a working email agent that:
- Polls Gmail for unread emails
- Generates contextual replies via Claude (with prompt caching)
- Saves as drafts or auto-sends based on configuration
- Runs locally or on a server

---

## Star Commands

| Command | What it does |
|---|---|
| `*onboard` | Run the full 7-phase onboarding to configure your email agent persona |
| `*review` | Surface pending improvement proposals for approval/rejection |
| `*reflect` | Manually trigger a friction review and generate improvement proposals |
| `*status` | Report environment health: spec coverage, open proposals, last activity |

---

## Key Files

| File | Purpose |
|---|---|
| `config.py` | **Primary customization point** — system prompt, reply mode, filters |
| `agent.py` | Main polling loop — run this to start the agent |
| `gmail_client.py` | Gmail API auth + read/send/draft helpers |
| `claude_agent.py` | Claude API call with prompt caching |
| `setup.sh` | Interactive initializer |
| `.env` | All configuration (never committed) |

---

## Configuration Priority

1. **System prompt** in `config.py` — defines the agent's persona and reply rules
2. **`.env` variables** — deployment mode, reply mode, filters
3. **Agent-onboarding docs** — `INTENT.md`, `SPECS/` — define long-term behavior

---

## Critical Rules for Working in This Repo

- `credentials.json` and `token.json` must NEVER be committed
- API keys must NEVER be hardcoded — always use `.env`
- Always test changes in draft mode before enabling auto-send
- The system prompt must be at least 1,024 tokens for prompt caching to activate
- When modifying `config.py`, run `verify_caching()` from `claude_agent.py` to confirm caching still works

---

## Onboarding Status

See `ONBOARDING_STATE.md` for current onboarding progress.

---

## Runtime

After completing a task, the self-improving runtime (see `RUNTIME.md`) will:
1. Review the task for friction (gaps, missing context, backtracking)
2. Generate improvement proposals into `IMPROVEMENT_QUEUE.md`
3. Surface a completion notice: `Task complete. Review queue has N pending proposal(s). Run *review to approve, reject, or modify.`

Always run `*review` after completing a task to keep the environment improving.
