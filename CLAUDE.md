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
- Filters emails by whitelist, blocklist, or allows all
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
| `config.py` | **Primary customization point** — SYSTEM_PROMPT, filter mode, reply mode |
| `agent.py` | Main polling loop + safety pre-flight check |
| `gmail_client.py` | Gmail API auth + read/send/draft helpers |
| `claude_agent.py` | Claude API call with prompt caching |
| `setup.sh` | Interactive setup wizard (non-technical friendly) |
| `.env` | All runtime configuration (never committed) |

---

## Email Filter Mode (Key Concept)

The `EMAIL_FILTER_MODE` setting controls which emails get a reply:

| Mode | Behavior | Use When |
|---|---|---|
| `whitelist` | Only reply to senders in `ONLY_REPLY_TO` | Starting out, or auto-send mode |
| `blocklist` | Reply to all except patterns in `IGNORE_SENDERS` | Public/support inbox |
| `all` | Reply to everything | Rarely — requires high confidence |

The pre-flight safety check in `agent.py` blocks unsafe combinations (e.g. auto-send + all mode).

---

## Configuration Priority

1. **System prompt** in `config.py` — defines the agent's persona and reply rules
2. **`.env` variables** — deployment mode, reply mode, filter mode
3. **Agent-onboarding docs** — `INTENT.md`, `SPECS/` — define long-term behavior

---

## Critical Rules for Working in This Repo

- `credentials.json` and `token.json` must NEVER be committed
- API keys must NEVER be hardcoded — always use `.env`
- Always test changes in draft mode before enabling auto-send
- Do NOT set `EMAIL_FILTER_MODE=all` with `REPLY_MODE=send` (blocked by pre-flight check)
- The system prompt must be at least 1,024 tokens for prompt caching to activate
- When modifying `config.py`, run `verify_caching()` from `claude_agent.py` to confirm caching still works

---

## Runtime

After every task, the self-improving runtime will surface improvement proposals.
Run `*review` to approve or reject them.
