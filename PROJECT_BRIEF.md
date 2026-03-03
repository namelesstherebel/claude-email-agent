# PROJECT_BRIEF.md

> Version: 1.0.0 | Status: Template (run *onboard to personalize)

---

## What This Is

**claude-email-agent** is a Python-based Gmail auto-reply agent powered by the Anthropic Claude API.

It is designed as an opinionated, production-ready template that can be initialized for any person or business that wants to automate email responses with AI.

---

## The Problem It Solves

Repetitive email responses consume significant time. Many inboxes receive the same types of questions repeatedly — FAQs, scheduling requests, support queries, acknowledgments — that follow predictable patterns. This agent handles those automatically, freeing up human attention for emails that genuinely require it.

---

## Architecture

Three-layer architecture:

**Layer 1 — Email Listener (Gmail API)**
Polls Gmail every N seconds for unread messages in INBOX. Filters out auto-generated emails, newsletters, and blocked senders.

**Layer 2 — Claude Brain (Anthropic SDK)**
Sends each email to Claude with a customized system prompt defining the reply persona. Uses prompt caching to reduce API costs by 90% on the system prompt after the first call.

**Layer 3 — Send or Draft**
Either saves the generated reply as a Gmail draft (default) or sends it immediately (opt-in). Applies a tracking label and marks the original as read.

---

## Key Design Decisions

- **Draft-first default**: Prevents runaway auto-replies during initial setup
- **Prompt caching required**: System prompt should be 1,024+ tokens for full cost savings
- **Polling over webhooks**: Simpler to deploy; Pub/Sub can be added later for production
- **Single file config**: All customization in `config.py` — no database, no UI
- **Agent-onboarding compatible**: Full onboarding infrastructure included for Claude Code users

---

## Deployment Options

| Option | Best For |
|---|---|
| `python3 agent.py` | Development and testing |
| `nohup python3 agent.py &` | Always-on local machine |
| systemd service | Linux server |
| Docker container | Any server, cloud VM |

---

## Status

This is a template. The following must be customized before use:
- [ ] `SYSTEM_PROMPT` in `config.py`
- [ ] `credentials.json` from Google Cloud Console
- [ ] `ANTHROPIC_API_KEY` in `.env`
- [ ] `REPLY_MODE` and `DEPLOY_MODE` in `.env`
