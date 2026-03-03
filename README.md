# Claude Email Agent

A smart, privacy-first email auto-reply agent powered by Claude AI.
Set it up once, and it monitors your inbox and drafts (or sends) replies automatically --
using your own writing style and judgment.

---

## Supported Email Providers

| Provider | Status | Auth Method |
|---|---|---|
| Gmail | Supported | Google OAuth2 (credentials.json) |
| Outlook / Microsoft 365 | Supported | Azure App Registration + MSAL |
| Yahoo Mail | Supported | App Password + IMAP |
| iCloud Mail | Supported | App-Specific Password + IMAP |
| Any IMAP/SMTP provider | Supported | App Password + IMAP |

> **Note:** A Google Cloud account is only required for Gmail users.
> An Azure account is only required for Outlook / Microsoft 365 users.
> All other providers use standard IMAP -- no cloud account needed.

---

## What It Does

- Monitors your inbox for new emails
- Uses Claude AI to read and understand each message
- Drafts a reply (or sends it automatically, your choice)
- Respects your filter rules -- only replies to the people you allow
- Runs locally on your computer or on a server
- Never stores your emails anywhere outside your own machine

---

## Before You Start

You need the following before running setup:

| Requirement | Who needs it | Where to get it |
|---|---|---|
| Anthropic API key | Everyone | https://console.anthropic.com/ |
| Google Cloud project + credentials.json | Gmail users only | https://console.cloud.google.com/ |
| Azure App Registration | Outlook users only | https://portal.azure.com/ |
| App password from your email provider | Yahoo / iCloud / IMAP users | See setup wizard instructions |
| Python 3.8 or newer | Everyone | https://python.org/downloads/ |

> **New to this?** Don't worry. The setup wizard walks you through every step.
> You do not need to be technical to get this running.

---

## Quick Start

### Step 1 -- Get the code

**Option A: Clone to a new folder with your own name**
```bash
git clone https://github.com/namelesstherebel/claude-email-agent.git my-email-agent
cd my-email-agent
```

**Option B: Clone with the default name**
```bash
git clone https://github.com/namelesstherebel/claude-email-agent.git
cd claude-email-agent
```

### Step 2 -- Run the setup wizard

```bash
bash setup.sh
```

The wizard will:
1. Ask which email provider you use
2. Walk you through the credentials setup for that provider
3. Ask for your Anthropic API key
4. Set your reply mode (draft or send)
5. Configure your email filters (who the agent replies to)
6. Set your agent's name and persona
7. Create your .env file automatically
8. Install all Python dependencies
9. Run a safety check before starting

### Step 3 -- Start the agent

```bash
python agent.py
```

---

## Safety Features

The agent is designed to be safe by default:

- **Draft mode by default** -- replies go to your Drafts folder, not your inbox
- **Whitelist by default** -- only replies to email addresses you approve
- **Pre-flight safety check** -- the agent refuses to start if dangerous settings are detected
- **No hardcoded secrets** -- all credentials live in your .env file, never in code
- **Gitignored by default** -- .env, credentials.json, and token.json are excluded from git

**Dangerous combinations that are blocked:**
- Auto-send + reply-to-all: blocked at startup
- Whitelist mode + empty whitelist: blocked at startup

---

## Email Filter Modes

Set EMAIL_FILTER_MODE in your .env file (the setup wizard sets this for you):

| Mode | What it does | Best for |
|---|---|---|
| whitelist | ONLY replies to addresses in ONLY_REPLY_TO | Starting out, auto-send, high safety |
| blocklist | Replies to everyone EXCEPT addresses in IGNORE_SENDERS | Public/customer-facing inboxes |
| all | Replies to every email (use with extreme caution) | Not recommended |

---

## Configuration Reference

All settings live in your .env file. Copy .env.example to get started.

| Variable | Default | Description |
|---|---|---|
| EMAIL_PROVIDER | gmail | Your email provider (gmail/outlook/yahoo/icloud/imap) |
| ANTHROPIC_API_KEY | (required) | Your Claude API key |
| REPLY_MODE | draft | draft saves to Drafts, send sends immediately |
| POLL_INTERVAL_SECONDS | 60 | How often to check for new email (seconds) |
| EMAIL_FILTER_MODE | whitelist | Who the agent responds to |
| ONLY_REPLY_TO | (empty) | Comma-separated whitelist of allowed senders |
| IGNORE_SENDERS | noreply@ etc | Comma-separated blocklist of senders to skip |
| AGENT_NAME | Email Assistant | Name used in Claude's system prompt |
| AGENT_PERSONA | (default) | Personality/instructions for Claude |
| DEPLOY_MODE | local | local or server |
| OUTLOOK_CLIENT_ID | (outlook only) | Azure app client ID |
| OUTLOOK_CLIENT_SECRET | (outlook only) | Azure app client secret |
| OUTLOOK_TENANT_ID | (outlook only) | Azure tenant ID (or consumers) |
| EMAIL_ADDRESS | (imap only) | Your email address |
| EMAIL_APP_PASSWORD | (imap only) | App password from your provider |
| IMAP_HOST | (imap only) | IMAP server hostname |
| IMAP_PORT | 993 | IMAP port |
| SMTP_HOST | (imap only) | SMTP server hostname |
| SMTP_PORT | 587 | SMTP port |

---

## Running on a Server

If you want the agent to run 24/7 without keeping your laptop open:

1. Run bash setup.sh and choose server as your deployment mode
2. The wizard will set up a systemd service (Linux) or give you Docker instructions
3. See the deploy/ folder for the Dockerfile and service file

---

## Troubleshooting

**credentials.json not found (Gmail)**
Download it from Google Cloud Console > APIs and Services > Credentials.
Save it in the same folder as agent.py.

**MSAL error or authentication failed (Outlook)**
Double-check your OUTLOOK_CLIENT_ID, OUTLOOK_CLIENT_SECRET, and OUTLOOK_TENANT_ID in .env.
Personal accounts (outlook.com, hotmail.com) should use OUTLOOK_TENANT_ID=consumers.

**IMAP login failed (Yahoo, iCloud, custom)**
Make sure you are using an app password, not your regular account password.
App passwords are different from your login password.

**Agent starts but sends no replies**
Check EMAIL_FILTER_MODE and ONLY_REPLY_TO in your .env.
If whitelist mode is on, the sender must be in ONLY_REPLY_TO.

**Want to reset everything?**
Delete your .env file and run bash setup.sh again.

---

## Project Structure

```
claude-email-agent/
  agent.py              -- Main agent loop
  email_client.py       -- Email provider abstraction (Gmail, Outlook, IMAP)
  gmail_client.py       -- Gmail-specific OAuth2 helpers
  claude_agent.py       -- Claude AI integration
  config.py             -- Config loader and filter logic
  setup.sh              -- Interactive setup wizard
  requirements.txt      -- Python dependencies
  .env.example          -- Template for your .env file
  .env                  -- Your actual config (gitignored)
  CLAUDE.md             -- Claude AI context and conventions
  deploy/               -- Docker and systemd deployment files
  SPECS/                -- Feature specifications
  CONTEXT/              -- Research and background notes
```

---

## License

MIT -- see LICENSE file.

---

> Built with the [agent-onboarding](https://github.com/namelesstherebel/agent-onboarding) framework.
