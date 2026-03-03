# Claude Email Agent

**An AI assistant that reads your Gmail and drafts (or sends) replies for you — powered by Claude AI.**

No coding knowledge required to get started. The setup wizard guides you through everything.

---

## What Does This Do?

Once set up, this agent:

1. Watches your Gmail inbox for new emails
2. Reads each email and generates a contextual, on-brand reply using Claude AI
3. Either **saves the reply as a Gmail draft** (so you can review before sending) or **sends it automatically** (once you trust it)
4. Labels processed emails in Gmail so you can track what it handled
5. Continuously improves over time as you give it more context

---

## Before You Start — What You'll Need

You need three things. None of them cost much:

| What | Where to get it | Cost |
|---|---|---|
| A **Google Cloud account** | [console.cloud.google.com](https://console.cloud.google.com) | Free |
| An **Anthropic API key** | [console.anthropic.com](https://console.anthropic.com) | ~$4-5/month at typical usage |
| **Python 3** installed | [python.org/downloads](https://www.python.org/downloads/) | Free |

The setup wizard will walk you through all three step by step.

---

## Quickstart (5 Steps)

### Step 1 — Get the code

**Option A: Clone with Git**
```bash
git clone https://github.com/YOUR_USERNAME/claude-email-agent.git
cd claude-email-agent
```

**Option B: Download ZIP**
- Click the green **Code** button on this page → **Download ZIP**
- Unzip it somewhere on your computer
- Open a terminal and `cd` into the folder

### Step 2 — Run the setup wizard

```bash
bash setup.sh
```

The wizard will ask you 8 simple questions and handle everything else. It takes about 10-15 minutes.

> **On Windows?** Use [Git Bash](https://gitforwindows.org/) or [WSL](https://docs.microsoft.com/en-us/windows/wsl/install) to run bash scripts.

### Step 3 — Customize your agent persona

Open `config.py` in any text editor and fill in the `SYSTEM_PROMPT` section.

This is like writing a briefing for a human assistant — the more detail you give, the better the replies:

```
SYSTEM_PROMPT = """
You are an email assistant for Sarah Chen at Bloom Consulting.

## Your Tone and Style
- Warm and professional
- Keep replies under 100 words when possible
- Always sign off: "Best, Sarah"

## Your Role
This inbox handles scheduling requests and project inquiries
for a small consulting firm.

## Business Hours
Monday through Friday, 9am to 6pm Pacific Time.
We typically respond within one business day.

## Common Questions
Q: What are your rates?
A: Our rates start at $150/hour. Happy to send a full proposal.

Q: Are you taking new clients?
A: Yes! We have capacity for 2-3 new projects starting next quarter.
"""
```

### Step 4 — Start the agent

```bash
python3 agent.py
```

You'll see it start up and begin watching your inbox. Press `Ctrl+C` to stop it.

### Step 5 — Review the drafts

Check your **Gmail Drafts folder**. You'll see Claude's replies waiting for you. Read a few, edit if needed, send the ones you like.

Once you're comfortable with the quality after a few days, you can switch to auto-send by changing `REPLY_MODE=send` in your `.env` file.

---

## Controlling Which Emails Get a Reply

This is one of the most important settings. You have three options:

### Option 1: Whitelist — Only reply to specific people ✅ Recommended

The agent **only responds to emails from addresses you list**. Everyone else is ignored.

Best for:
- Starting out (safest option)
- Using auto-send mode
- Responding only to your team, clients, or known contacts

Set in your `.env` file:
```
EMAIL_FILTER_MODE=whitelist
ONLY_REPLY_TO=alice@company.com, bob@company.com, @trustedcorp.com
```

> You can use partial matches like `@trustedcorp.com` to whitelist an entire domain.

### Option 2: Blocklist — Reply to everyone except spam/newsletters

The agent replies to **all emails except** the ones you've blocked.

Best for:
- Customer support inboxes
- Public-facing email addresses
- When you want broad coverage

Set in your `.env` file:
```
EMAIL_FILTER_MODE=blocklist
IGNORE_SENDERS=noreply@,no-reply@,newsletter@,unsubscribe@
```

> The agent always blocks obvious auto-senders (mailer-daemon, postmaster, etc.) regardless of mode.

### Option 3: All emails — No filter

Replies to everything. **Not recommended** unless you know exactly what you're doing.

```
EMAIL_FILTER_MODE=all
```

---

## Draft Mode vs. Auto-Send

| | Draft Mode | Auto-Send |
|---|---|---|
| What happens | Claude writes the reply, saves it to Drafts | Claude writes AND sends the reply |
| You review? | Yes — you decide whether to send | No — it goes out automatically |
| Recommended for | Starting out, any inbox | Only after reviewing drafts for days/weeks |
| How to set | `REPLY_MODE=draft` (default) | `REPLY_MODE=send` |

**Always start in draft mode.** Switch to auto-send only after you've reviewed at least a week of draft replies and are happy with the quality.

---

## Running It in the Background

### On your computer (keep it running after closing terminal)
```bash
nohup python3 agent.py > agent.log 2>&1 &
```
To stop it: `pkill -f agent.py`

### On a Linux server (runs 24/7, restarts automatically)

1. Edit the paths in `deploy/claude-email-agent.service`
2. Install it:
```bash
sudo cp deploy/claude-email-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable claude-email-agent
sudo systemctl start claude-email-agent
```
3. Check it's running: `sudo systemctl status claude-email-agent`
4. View logs: `sudo journalctl -u claude-email-agent -f`

### With Docker
```bash
docker build -t claude-email-agent .
docker run -d \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json \
  -v $(pwd)/token.json:/app/token.json \
  claude-email-agent
```

---

## Improving Your Agent Over Time

This repo includes [agent-onboarding](https://github.com/namelesstherebel/agent-onboarding) infrastructure. If you use **Claude Code**, you can run a guided 7-phase setup that deeply configures your agent:

```
*onboard
```

After any task, the agent surfaces suggestions for improvement:

```
*review
```

---

## All Settings Reference

Edit these in your `.env` file (created by setup.sh):

| Setting | What it does | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Claude AI key | (required) |
| `REPLY_MODE` | `draft` or `send` | `draft` |
| `EMAIL_FILTER_MODE` | `whitelist`, `blocklist`, or `all` | `whitelist` |
| `ONLY_REPLY_TO` | Emails to respond to (whitelist mode) | (empty) |
| `IGNORE_SENDERS` | Patterns to never reply to | spam/auto-senders |
| `POLL_INTERVAL_SECONDS` | How often to check Gmail | `60` |
| `LABEL_AFTER_REPLY` | Gmail label to tag processed emails | `AI-Replied` |
| `MODEL` | Claude model | `claude-haiku-4-5` |
| `DEPLOY_MODE` | `local` or `server` | `local` |

---

## Safety Checklist

Before going live, make sure you can check all of these:

- [ ] I started in **draft mode** and reviewed replies for several days
- [ ] I'm using a **test Gmail account** first (not my main inbox)
- [ ] I set up a **whitelist** or at minimum a blocklist
- [ ] My **credentials.json** and **token.json** are in .gitignore (never committed)
- [ ] My **API key** is in .env, not hardcoded in any file
- [ ] I've customized the **SYSTEM_PROMPT** in config.py with real context
- [ ] If using auto-send, I have a **whitelist** set

---

## Cost

At 100 emails per day using `claude-haiku-4-5` with prompt caching: **under $5/month**.

This is because the agent uses a technique called **prompt caching** — your system prompt (the briefing you write) is cached by Anthropic and reused at 10% of the normal cost for every email after the first.

The longer and more detailed your system prompt, the bigger the savings. A thorough 2,000-word briefing costs almost the same as a short one.

---

## Troubleshooting

**"No module named X"** — Run `pip3 install -r requirements.txt`

**"credentials.json not found"** — Make sure you downloaded and placed it in the project folder (see setup.sh Step 7)

**"Token has been expired"** — Delete `token.json` and run the agent again. It will re-open the browser to re-authorize.

**"Access blocked: app not verified"** — In Google Cloud Console, add your Gmail address as a test user under APIs & Services > OAuth consent screen > Test users.

**Agent not responding to emails** — Check `agent.log` for errors. Also confirm your `EMAIL_FILTER_MODE` and `ONLY_REPLY_TO` settings — the email may be getting filtered.

**Replies sound generic** — Add more detail to `SYSTEM_PROMPT` in `config.py`. Include FAQs, example replies, and specific business context.

---

## File Structure

```
claude-email-agent/
├── agent.py             # Main loop — run this to start the agent
├── gmail_client.py      # Gmail API helpers
├── claude_agent.py      # Claude AI reply generation
├── config.py            # ⭐ Main config — customize SYSTEM_PROMPT here
├── setup.sh             # Setup wizard — run this first
├── requirements.txt     # Python packages
├── .env.example         # Settings template (copy to .env)
├── .gitignore           # Keeps secrets out of git
├── deploy/
│   ├── Dockerfile                    # Docker deployment
│   └── claude-email-agent.service    # Linux systemd service
├── CLAUDE.md            # Agent context for Claude Code users
├── INTENT.md            # Agent trade-off rules
├── SPECS/               # Technical specs for each feature
└── CONTEXT/
    └── email-agent-research.md  # Architecture and cost details
```

---

## License

MIT
