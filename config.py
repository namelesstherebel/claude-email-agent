import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# Deployment mode
# ─────────────────────────────────────────
# "local"  — run on your machine
# "server" — run as a systemd service or Docker container
DEPLOY_MODE = os.getenv("DEPLOY_MODE", "local")

# ─────────────────────────────────────────
# Reply mode
# ─────────────────────────────────────────
# "draft" — save Claude's reply as a Gmail draft (START HERE — strongly recommended)
# "send"  — automatically send the reply (only enable after reviewing drafts for several days)
REPLY_MODE = os.getenv("REPLY_MODE", "draft")

# ─────────────────────────────────────────
# Polling interval (seconds)
# ─────────────────────────────────────────
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

# ─────────────────────────────────────────
# Email filter mode
# ─────────────────────────────────────────
# This controls WHICH emails the agent responds to.
#
# "whitelist" — ONLY respond to senders listed in ONLY_REPLY_TO
#               Most safe. Recommended when starting or using auto-send.
#               Example use: only respond to your team or specific clients.
#
# "blocklist" — Respond to EVERYONE except patterns in IGNORE_SENDERS
#               Good for customer support or public-facing inboxes.
#               Still blocks newsletters and auto-generated messages.
#
# "all"       — Respond to every email. Not recommended.
#               Use only if you have very high confidence in your setup.
EMAIL_FILTER_MODE = os.getenv("EMAIL_FILTER_MODE", "blocklist")

# ─────────────────────────────────────────
# Whitelist: only reply to these senders
# ─────────────────────────────────────────
# Used when EMAIL_FILTER_MODE = "whitelist"
# Can be full email addresses OR partial matches (e.g. "@mycompany.com")
# Set via .env as a comma-separated list:
#   ONLY_REPLY_TO=alice@example.com,bob@example.com,@trustedcorp.com
_only_reply_raw = os.getenv("ONLY_REPLY_TO", "")
ONLY_REPLY_TO = [e.strip().lower() for e in _only_reply_raw.split(",") if e.strip()]

# ─────────────────────────────────────────
# Blocklist: never reply to these patterns
# ─────────────────────────────────────────
# Used when EMAIL_FILTER_MODE = "blocklist" or "all"
# These are substring matches — if any pattern appears in the sender address,
# the email is skipped.
_ignore_raw = os.getenv(
    "IGNORE_SENDERS",
    "noreply@,no-reply@,mailer-daemon@,postmaster@,donotreply@"
)
IGNORE_SENDERS = [p.strip().lower() for p in _ignore_raw.split(",") if p.strip()]

# ─────────────────────────────────────────
# Gmail label applied after processing
# ─────────────────────────────────────────
# The agent will apply this Gmail label to every email it processes.
# Leave empty to skip labeling.
LABEL_AFTER_REPLY = os.getenv("LABEL_AFTER_REPLY", "AI-Replied")

# ─────────────────────────────────────────
# Claude model
# ─────────────────────────────────────────
# claude-haiku-4-5  → fastest, cheapest  (~$4-5/mo at 100 emails/day) ✅ recommended
# claude-sonnet-4-6 → higher quality, moderate cost
# claude-opus-4-6   → highest quality, highest cost
MODEL = os.getenv("MODEL", "claude-haiku-4-5")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# ─────────────────────────────────────────
# System prompt — CUSTOMIZE THIS
# ─────────────────────────────────────────
# This is the single most important thing to customize.
# Think of this as the "briefing document" you'd give a human assistant.
# The more context you provide:
#   - The more accurate the replies
#   - The more on-brand the tone
#   - The less often the agent will need to ask for clarification
#
# With prompt caching enabled, adding more detail here is nearly FREE
# after the first API call. So go into as much detail as you want.
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
