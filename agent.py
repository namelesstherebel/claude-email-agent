"""
agent.py
Main polling loop — monitors email inbox and generates replies via Claude.
Supports Gmail, Outlook, Yahoo, iCloud, and any IMAP/SMTP provider.
"""

import time
import logging
import sys
import os

from dotenv import load_dotenv
load_dotenv()

from claude_agent import generate_reply
from config import (
    POLL_INTERVAL_SECONDS,
    REPLY_MODE,
    EMAIL_FILTER_MODE,
    ONLY_REPLY_TO,
    IGNORE_SENDERS,
    LABEL_AFTER_REPLY,
)

# ─── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent.log"),
    ],
)
logger = logging.getLogger(__name__)


# ─── Provider-aware client factory ───────────────────────────────────────────

def build_email_client():
    """
    Instantiate the correct EmailClient subclass based on EMAIL_PROVIDER in .env.

    Gmail    -> GmailClient   (Google API + OAuth2, uses gmail_client.py)
    Outlook  -> OutlookClient (Microsoft Graph + MSAL)
    Yahoo/iCloud/custom -> IMAPClient (stdlib imaplib/smtplib)
    """
    provider = os.environ.get("EMAIL_PROVIDER", "gmail").lower().strip()

    if provider == "gmail":
        from email_client import GmailClient
        return GmailClient()

    elif provider == "outlook":
        from email_client import OutlookClient
        return OutlookClient()

    elif provider in ("yahoo", "icloud", "imap"):
        from email_client import IMAPClient
        return IMAPClient()

    else:
        logger.warning(
            f"Unknown EMAIL_PROVIDER '{provider}'. Falling back to IMAPClient. "
            "Set EMAIL_PROVIDER to: gmail, outlook, yahoo, icloud, or imap."
        )
        from email_client import IMAPClient
        return IMAPClient()


# ─── Safety pre-flight check ─────────────────────────────────────────────────

def preflight_safety_check():
    """
    Run safety checks before starting the polling loop.
    Warns on risky configs and hard-blocks unsafe combinations.
    """
    issues = []
    warnings = []

    if REPLY_MODE == "send" and EMAIL_FILTER_MODE == "all":
        issues.append(
            "UNSAFE: auto-send is enabled with EMAIL_FILTER_MODE=all. "
            "The agent would auto-reply to EVERY email including newsletters and spam. "
            "Set EMAIL_FILTER_MODE=whitelist or blocklist, or switch to REPLY_MODE=draft."
        )

    if REPLY_MODE == "send" and EMAIL_FILTER_MODE == "blocklist":
        warnings.append(
            "Auto-send is on with blocklist mode. The agent will reply to all emails "
            "that don't match your blocklist. Consider using whitelist mode for more control."
        )

    if EMAIL_FILTER_MODE == "whitelist" and not ONLY_REPLY_TO:
        issues.append(
            "EMAIL_FILTER_MODE=whitelist but ONLY_REPLY_TO is empty. "
            "The agent would reply to NO emails. "
            "Add senders to ONLY_REPLY_TO in .env, or change EMAIL_FILTER_MODE."
        )

    for w in warnings:
        logger.warning(f"⚠  {w}")

    if issues:
        for issue in issues:
            logger.error(f"🚫 SAFETY BLOCK: {issue}")
        logger.error(
            "Agent did not start due to unsafe configuration. "
            "Fix the issues above in your .env file and restart."
        )
        sys.exit(1)


# ─── Email filtering ─────────────────────────────────────────────────────────

def should_process(email: dict) -> bool:
    """
    Return True if this email should receive a reply.

    whitelist — only reply if sender matches something in ONLY_REPLY_TO
    blocklist — reply to all EXCEPT senders matching IGNORE_SENDERS
    all       — reply to everything (still skips hard-blocked patterns as a safety floor)
    """
    sender = email.get("sender", "").lower()

    if EMAIL_FILTER_MODE == "whitelist":
        if not any(allowed in sender for allowed in ONLY_REPLY_TO):
            logger.debug(f"Skipping — not in whitelist: {sender}")
            return False
        # Still apply blocklist as secondary safety layer
        for pattern in IGNORE_SENDERS:
            if pattern in sender:
                logger.debug(f"Skipping — blocklist match '{pattern}': {sender}")
                return False
        return True

    elif EMAIL_FILTER_MODE == "blocklist":
        for pattern in IGNORE_SENDERS:
            if pattern in sender:
                logger.debug(f"Skipping — blocklist match '{pattern}': {sender}")
                return False
        return True

    else:  # "all" — apply blocklist as minimum safety floor
        for pattern in IGNORE_SENDERS:
            if pattern in sender:
                logger.debug(f"Skipping — blocklist match '{pattern}': {sender}")
                return False
        return True


# ─── Email processing ────────────────────────────────────────────────────────

def process_email(client, email: dict) -> None:
    """
    Generate a reply for a single email and either draft or send it.
    Works identically for all providers — the EmailClient handles the differences.
    """
    subject   = email["subject"]
    sender    = email["sender"]
    reply_to  = email.get("reply_to", sender)
    body      = email["body"]
    thread_id = email["thread_id"]
    msg_id    = email["id"]

    logger.info(f"Processing: '{subject}' from {sender}")

    try:
        reply_text = generate_reply(subject, body, sender)
    except Exception as e:
        logger.error(f"Failed to generate reply for '{subject}': {e}")
        return

    if REPLY_MODE == "send":
        client.send_reply(reply_to, subject, reply_text, thread_id)
        logger.info(f"✉  Reply SENT to {reply_to}")
    else:
        client.create_draft(reply_to, subject, reply_text, thread_id)
        logger.info(f"📋  Draft CREATED for {reply_to}")

    client.mark_read(msg_id)

    if LABEL_AFTER_REPLY:
        try:
            client.apply_label(msg_id, LABEL_AFTER_REPLY)
        except Exception:
            # Non-Gmail clients may not support labelling — silently skip
            pass


# ─── Main polling loop ───────────────────────────────────────────────────────

def run_polling_loop():
    """
    Main loop. Runs indefinitely, polling for new emails every POLL_INTERVAL_SECONDS.
    """
    preflight_safety_check()

    provider = os.environ.get("EMAIL_PROVIDER", "gmail").lower()

    logger.info("=" * 55)
    logger.info("  Claude Email Agent starting...")
    logger.info(f"  Provider:      {provider.upper()}")
    logger.info(f"  Reply mode:    {REPLY_MODE.upper()}")
    logger.info(f"  Filter mode:   {EMAIL_FILTER_MODE.upper()}")
    if EMAIL_FILTER_MODE == "whitelist":
        logger.info(f"  Whitelist:     {ONLY_REPLY_TO}")
    elif EMAIL_FILTER_MODE == "blocklist":
        logger.info(f"  Blocklist:     {IGNORE_SENDERS}")
    logger.info(f"  Poll interval: {POLL_INTERVAL_SECONDS}s")
    logger.info(f"  Label:         {LABEL_AFTER_REPLY or 'none'}")
    logger.info("=" * 55)

    client   = build_email_client()
    seen_ids = set()

    while True:
        try:
            emails = client.get_unread()
            new_emails = [e for e in emails if e["id"] not in seen_ids]

            if not new_emails:
                logger.debug(f"No new emails. Sleeping {POLL_INTERVAL_SECONDS}s...")
            else:
                logger.info(f"Found {len(new_emails)} new email(s).")

            for email in new_emails:
                seen_ids.add(email["id"])
                if should_process(email):
                    process_email(client, email)
                else:
                    logger.debug(f"Skipped: {email.get('sender','?')} — {email.get('subject','?')}")

        except KeyboardInterrupt:
            logger.info("Agent stopped by user (Ctrl+C).")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            logger.info(f"Retrying in {POLL_INTERVAL_SECONDS}s...")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_polling_loop()
