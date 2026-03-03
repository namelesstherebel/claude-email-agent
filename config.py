import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# Deployment mode
# ─────────────────────────────────────────
# "local"  — run on your machine (polling loop via cron/terminal/nohup)
# "server" — run as a systemd service or Docker container
DEPLOY_MODE = os.getenv("DEPLOY_MODE", "local")

# ─────────────────────────────────────────
# Reply mode
# ─────────────────────────────────────────
# "draft" — save Claude's reply as a Gmail draft (RECOMMENDED to start)
# "send"  — automatically send the reply (enable only after reviewing drafts)
REPLY_MODE = os.getenv("REPLY_MODE", "draft")

# ─────────────────────────────────────────
# Polling interval (seconds)
# ─────────────────────────────────────────
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

# ─────────────────────────────────────────
# Sender filters
# ─────────────────────────────────────────
# Whitelist: only reply to these senders (leave empty to reply to all)
# Example: ONLY_REPLY_TO = ["alice@example.com", "bob@example.com"]
_only_reply_raw = os.getenv("ONLY_REPLY_TO", "")
ONLY_REPLY_TO = [e.strip() for e in _only_reply_raw.split(",") if e.strip()]

# Blocklist: never reply to senders matching these patterns
_ignore_raw = os.getenv("IGNORE_SENDERS", "noreply@,no-reply@,mailer-daemon@,postmaster@")
IGNORE_SENDERS = [p.strip() for p in _ignore_raw.split(",") if p.strip()]

# ─────────────────────────────────────────
# Gmail label applied after processing
# ─────────────────────────────────────────
LABEL_AFTER_REPLY = os.getenv("LABEL_AFTER_REPLY", "AI-Replied")

# ─────────────────────────────────────────
# Claude model
# ─────────────────────────────────────────
# claude-haiku-4-5  → fastest, cheapest  (~$4-5/mo at 100 emails/day) ✅ recommended
# claude-sonnet-4-6 → more nuanced replies, higher cost
# claude-opus-4-6   → highest quality, highest cost
MODEL = os.getenv("MODEL", "claude-haiku-4-5")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# ─────────────────────────────────────────
# System prompt — CUSTOMIZE THIS
# ─────────────────────────────────────────
# This is the most important customization point.
# The more context you provide, the better the replies.
# With prompt caching enabled, extra length is nearly free after the first call.
#
# Minimum 1,024 tokens required for caching to activate.
# A detailed prompt with persona + FAQs + policies easily exceeds this.

SYSTEM_PROMPT = """
You are an email assistant for [YOUR NAME / COMPANY NAME].

## Your Tone and Style
- Professional but warm
- Concise — keep replies under 150 words unless the email genuinely requires more
- Always use first-person ("I" not "We") unless instructed otherwise
- Never use filler phrases like "I hope this email finds you well"

## Your Role
[Describe what this inbox is for — e.g., customer support, scheduling,
sales inquiries, personal correspondence, etc.]

## Rules
- Never promise something you cannot confirm (e.g., do not commit to deadlines)
- If you do not have enough context to answer, politely ask for clarification
- Always end with a professional sign-off: "Best regards, [YOUR NAME]"
- Do NOT include a subject line in your reply — just the body text
- Do not mention that you are an AI unless directly asked
- Skip auto-reply indicators (Out of Office, Do Not Reply, etc.)

## Context About This Person / Business
[Insert static facts the agent should always know:]
- Business hours: Monday–Friday, 9am–5pm [TIMEZONE]
- [Add FAQs, pricing, policies, common responses, etc.]
- [The more detail here, the more accurate the replies]

## Examples of Good Replies
[Optional but highly recommended — add 2-3 example email/reply pairs]

Example 1:
Email: "Hi, what are your hours?"
Reply: "Hi [Name], we're open Monday through Friday, 9am to 5pm EST. Feel free to reach out any time and I'll get back to you during business hours. Best regards, [YOUR NAME]"
"""
