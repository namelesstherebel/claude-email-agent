# CLAUDE.md -- Claude Email Agent

This file gives Claude AI context about this project whenever it is opened in an AI-assisted editor.

---

## Project Purpose

This is a template repository for setting up a personal email auto-reply agent powered by Claude AI.
Users clone this repo, run the setup wizard, and get a working AI email agent in minutes.
It supports multiple email providers and deploys locally or on a server.

---

## Architecture

Three-layer design:

1. **Email Client Layer** (email_client.py) -- reads and sends emails
   - GmailClient: Gmail via Google OAuth2 + Gmail API
   - OutlookClient: Outlook / Microsoft 365 via Microsoft Graph API (MSAL)
   - IMAPClient: Any provider via imaplib/smtplib (Yahoo, iCloud, custom)
   - All three expose identical interface: get_unread(), send_reply(), create_draft(), mark_read()

2. **Claude Brain** (claude_agent.py) -- generates replies using Anthropic API
   - Uses prompt caching (cache_control ephemeral) on system prompt
   - Model: claude-haiku-4-5 for speed and cost efficiency

3. **Agent Loop** (agent.py) -- orchestrates polling, filtering, and actions
   - Runs pre-flight safety check before any operations
   - Respects EMAIL_FILTER_MODE (whitelist / blocklist / all)
   - Respects REPLY_MODE (draft / send)

---

## Supported Email Providers

| Provider | Client Class | Auth |
|---|---|---|
| Gmail | GmailClient | Google OAuth2 (credentials.json + token.json) |
| Outlook / Microsoft 365 | OutlookClient | Azure MSAL (client_id, client_secret, tenant_id) |
| Yahoo Mail | IMAPClient | App password + IMAP |
| iCloud Mail | IMAPClient | App-specific password + IMAP |
| Any IMAP provider | IMAPClient | App password + IMAP |

Provider is selected during setup.sh and stored as EMAIL_PROVIDER in .env.
agent.py uses build_email_client() to instantiate the correct client.

---

## Key Settings (all in .env)

| Variable | Values | Notes |
|---|---|---|
| EMAIL_PROVIDER | gmail / outlook / yahoo / icloud / imap | Set by setup.sh |
| REPLY_MODE | draft / send | Default: draft |
| EMAIL_FILTER_MODE | whitelist / blocklist / all | Default: whitelist |
| ONLY_REPLY_TO | comma-separated emails | Used when whitelist mode |
| IGNORE_SENDERS | comma-separated patterns | Used when blocklist mode |
| ANTHROPIC_API_KEY | sk-ant-... | Required |
| AGENT_PERSONA | free text | System prompt instructions |
| OUTLOOK_CLIENT_ID | UUID | Outlook only |
| OUTLOOK_CLIENT_SECRET | string | Outlook only |
| OUTLOOK_TENANT_ID | UUID or consumers | Outlook only |
| EMAIL_ADDRESS | email address | IMAP providers only |
| EMAIL_APP_PASSWORD | string | IMAP providers only |
| IMAP_HOST | hostname | IMAP providers only |
| SMTP_HOST | hostname | IMAP providers only |

---

## Safety Rules

NEVER do any of the following:
- Commit .env, credentials.json, or token.json to git (gitignored)
- Hardcode API keys, passwords, or secrets in any source file
- Start the agent with REPLY_MODE=send and EMAIL_FILTER_MODE=all (blocked by preflight)
- Start the agent with EMAIL_FILTER_MODE=whitelist and empty ONLY_REPLY_TO (blocked by preflight)
- Break the existing Gmail flow -- GmailClient must preserve all existing behavior

---

## File Map

- agent.py -- main loop, build_email_client() factory, preflight_safety_check()
- email_client.py -- EmailClient base class + GmailClient, OutlookClient, IMAPClient
- gmail_client.py -- Gmail OAuth2 helpers (imported by GmailClient)
- claude_agent.py -- Anthropic SDK wrapper
- config.py -- loads .env, filter logic
- setup.sh -- interactive 9-step setup wizard
- .env.example -- template with all variables documented
- deploy/ -- Dockerfile + systemd service for server deployment
- SPECS/ -- feature specifications (SPEC-001 through SPEC-005)

---

## Onboarding Infrastructure

This repo was bootstrapped with the agent-onboarding framework:
https://github.com/namelesstherebel/agent-onboarding

Key docs produced by onboarding:
- INTENT.md -- project goals and north star
- PROJECT_BRIEF.md -- stakeholder-facing overview
- SPEC_INVENTORY.md -- list of all specifications
- RUNTIME.md -- how to run and deploy
- IMPROVEMENT_QUEUE.md -- backlog of future improvements
- ONBOARDING_STATE.md -- onboarding phase tracker
