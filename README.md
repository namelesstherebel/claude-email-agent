# Claude Email Agent

> A smart, self-improving email auto-reply agent powered by Claude AI and the Gmail API — with built-in agent-onboarding infrastructure for context-aware, continuously improving replies.

---

## What This Is

This repo is a **ready-to-initialize template** for building a Claude-powered email agent. Once set up, it:

- Monitors your Gmail inbox for new emails
- Uses Claude (with prompt caching) to draft contextual, persona-aware replies
- Saves replies as **drafts** (default) or **auto-sends** them (opt-in)
- Runs **locally** or on a **server** (systemd service or Docker)
- Includes full **agent-onboarding** infrastructure so the agent understands your inbox, persona, and goals — and improves over time

---

## Quick Start

### 1. Clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/claude-email-agent.git
cd claude-email-agent
```

### 2. Run the initializer

```bash
bash setup.sh
```

This will:
- Ask whether you want to run **locally** or on a **server**
- Ask whether the agent should **draft** replies or **auto-send** them
- Install Python dependencies
- Guide you through Google OAuth setup
- Write your choices to `.env`

### 3. Add your credentials

- Place your `credentials.json` (Google OAuth2) in the project root
- Add your `ANTHROPIC_API_KEY` to `.env`

### 4. Customize your agent persona

Edit `config.py` — specifically the `SYSTEM_PROMPT` block. The more context you give it (your name, role, business, FAQs, policies), the better the replies.

### 5. Start the agent

**Local (foreground):**
```bash
python agent.py
```

**Local (background):**
```bash
nohup python agent.py &
```

**Server (systemd service):**
```bash
sudo cp deploy/claude-email-agent.service /etc/systemd/system/
sudo systemctl enable claude-email-agent
sudo systemctl start claude-email-agent
```

**Docker:**
```bash
docker build -t claude-email-agent .
docker run -d --env-file .env -v $(pwd)/credentials.json:/app/credentials.json -v $(pwd)/token.json:/app/token.json claude-email-agent
```

---

## Agent Onboarding

This repo includes the [agent-onboarding](https://github.com/namelesstherebel/agent-onboarding) infrastructure. If you use **Claude Code**, run the full onboarding workflow to deeply configure your agent:

```
*onboard
```

This walks you through 7 phases and produces `CLAUDE.md`, `INTENT.md`, `PROJECT_BRIEF.md`, `SPEC_INVENTORY.md`, and a full `SPECS/` directory — giving your agent rich context about your inbox and persona.

After any task, the runtime surfaces improvement proposals:
```
*review
```

See [CLAUDE.md](./CLAUDE.md) for agent commands and full context.

---

## Configuration Options

All settings live in `.env` and `config.py`.

| Setting | Options | Default |
|---|---|---|
| `REPLY_MODE` | `draft` / `send` | `draft` |
| `DEPLOY_MODE` | `local` / `server` | `local` |
| `POLL_INTERVAL_SECONDS` | Any integer | `60` |
| `ONLY_REPLY_TO` | Comma-separated emails | (all) |
| `IGNORE_SENDERS` | Comma-separated patterns | `noreply@,no-reply@` |
| `LABEL_AFTER_REPLY` | Any Gmail label name | `AI-Replied` |
| `MODEL` | Claude model name | `claude-haiku-4-5` |

---

## Repo Structure

```
claude-email-agent/
├── agent.py                         # Main polling loop
├── gmail_client.py                  # Gmail API auth + read/send/draft helpers
├── claude_agent.py                  # Claude API calls + prompt caching
├── config.py                        # System prompt, filters, settings
├── setup.sh                         # Interactive initializer
├── requirements.txt
├── .env.example
├── .gitignore
├── deploy/
│   ├── claude-email-agent.service   # systemd unit file
│   └── Dockerfile
├── CLAUDE.md                        # Agent context loaded by Claude Code
├── INTENT.md                        # Agent intent and trade-off rules
├── PROJECT_BRIEF.md                 # Project overview
├── SPEC_INVENTORY.md                # Task inventory and spec queue
├── RUNTIME.md                       # Self-improving runtime
├── IMPROVEMENT_QUEUE.md             # Proposal queue
├── ONBOARDING_STATE.md              # Onboarding progress tracker
├── CONTEXT/
│   └── email-agent-research.md     # Full research doc and cost breakdown
└── SPECS/
    ├── SPEC-001-gmail-polling.md
    ├── SPEC-002-claude-reply.md
    └── SPEC-003-send-or-draft.md
```

---

## Safety Checklist

- Start in **draft mode** — review replies for a few days before enabling auto-send
- Use a **test Gmail account** first, not your main inbox
- **Never commit** `credentials.json` or `token.json` — they are in `.gitignore`
- Store all API keys in `.env`, never hardcoded
- Sender whitelisting (`ONLY_REPLY_TO`) is strongly recommended for auto-send
- Skip newsletters by checking for `List-Unsubscribe` headers
- Verify prompt caching is active via `usage.cache_read_input_tokens` on the second call

---

## Cost

Using `claude-haiku-4-5` with prompt caching at 100 emails/day: **~$4-5/month**.

See [CONTEXT/email-agent-research.md](./CONTEXT/email-agent-research.md) for the full cost breakdown and model comparison.

---

## Requirements

- Python 3.9+
- Google Cloud project with Gmail API enabled
- Anthropic API key ([get one here](https://console.anthropic.com))
- Gmail account

---

## License

MIT
