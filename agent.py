"""
agent.py
Main polling loop — monitors Gmail for new emails and generates replies via Claude.
"""

import time
import logging
import sys

from gmail_client import (
    get_gmail_service,
    get_unread_emails,
    create_draft,
    send_reply,
    mark_as_read,
    apply_label,
)
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


def preflight_safety_check():
    """
    Run safety checks before starting the polling loop.
    Warns the user about risky configurations and blocks unsafe combinations.
    """
    issues = []
    warnings = []

    # Block: auto-send with no filter is very risky
    if REPLY_MODE == "send" and EMAIL_FILTER_MODE == "all":
        issues.append(
            "UNSAFE: auto-send is enabled with EMAIL_FILTER_MODE=all. "
            "This means the agent will auto-reply to EVERY email including "
            "newsletters, spam, and system messages. "
            "Set EMAIL_FILTER_MODE=whitelist or blocklist, or switch to REPLY_MODE=draft."
        )

    # Warn: auto-send with blocklist (riskier than whitelist)
    if REPLY_MODE == "send" and EMAIL_FILTER_MODE == "blocklist":
        warnings.append(
            "Auto-send is on with blocklist mode. The agent will reply to all emails "
            "that don't match your blocklist. Consider using whitelist mode for more control."
        )

    # Warn: whitelist mode with empty whitelist
    if EMAIL_FILTER_MODE == "whitelist" and not ONLY_REPLY_TO:
        issues.append(
            "EMAIL_FILTER_MODE is set to 'whitelist' but ONLY_REPLY_TO is empty. "
            "The agent would reply to NO emails. "
            "Add senders to ONLY_REPLY_TO in your .env file, or change EMAIL_FILTER_MODE."
        )

    # Print warnings
    for w in warnings:
        logger.warning(f"⚠  {w}")

    # Print and block on issues
    if issues:
        for issue in issues:
            logger.error(f"🚫 SAFETY BLOCK: {issue}")
        logger.error(
            "Agent did not start due to unsafe configuration. "
            "Fix the issues above in your .env file and restart."
        )
        sys.exit(1)


def should_process(email):
    """
    Return True if this email should receive a reply.

    Filter logic depends on EMAIL_FILTER_MODE:

    whitelist — ONLY reply if sender matches something in ONLY_REPLY_TO
    blocklist — Reply to all EXCEPT senders matching IGNORE_SENDERS patterns
    all       — Reply to everything (no filter applied)
    """
    sender = email.get("sender", "").lower()

    if EMAIL_FILTER_MODE == "whitelist":
        # Only process if sender matches at least one whitelist entry
        if not any(allowed in sender for allowed in ONLY_REPLY_TO):
            logger.debug(f"Skipping — not in whitelist: {sender}")
            return False
        # Still check blocklist even in whitelist mode (safety layer)
        for pattern in IGNORE_SENDERS:
            if pattern in sender:
                logger.debug(f"Skipping — blocklist match '{pattern}': {sender}")
                return False
        return True

    elif EMAIL_FILTER_MODE == "blocklist":
        # Skip if sender matches any blocklist pattern
        for pattern in IGNORE_SENDERS:
            if pattern in sender:
                logger.debug(f"Skipping — blocklist match '{pattern}': {sender}")
                return False
        return True

    else:  # EMAIL_FILTER_MODE == "all"
        # Still apply blocklist as a minimum safety layer
        for pattern in IGNORE_SENDERS:
            if pattern in sender:
                logger.debug(f"Skipping — blocklist match '{pattern}': {sender}")
                return False
        return True


def process_email(service, email):
    """
    Generate a reply for a single email and either draft or send it.
    """
    subject = email["subject"]
    sender = email["sender"]
    reply_to = email["reply_to"]
    body = email["body"]
    thread_id = email["threadId"]
    msg_id = email["id"]

    logger.info(f"Processing: '{subject}' from {sender}")

    try:
        reply_text = generate_reply(subject, body, sender)
    except Exception as e:
        logger.error(f"Failed to generate reply for '{subject}': {e}")
        return

    if REPLY_MODE == "send":
        send_reply(service, reply_to, subject, reply_text, thread_id)
        logger.info(f"✉  Reply SENT to {reply_to}")
    else:
        create_draft(service, reply_to, subject, reply_text, thread_id)
        logger.info(f"📋  Draft CREATED for {reply_to}")

    # Mark original as read and apply tracking label
    mark_as_read(service, msg_id)
    if LABEL_AFTER_REPLY:
        apply_label(service, msg_id, LABEL_AFTER_REPLY)


def run_polling_loop():
    """
    Main polling loop. Runs indefinitely, checking for new emails every
    POLL_INTERVAL_SECONDS seconds.
    """
    # Safety check before doing anything
    preflight_safety_check()

    logger.info("=" * 55)
    logger.info("  Claude Email Agent starting...")
    logger.info(f"  Reply mode:    {REPLY_MODE.upper()}")
    logger.info(f"  Filter mode:   {EMAIL_FILTER_MODE.upper()}")
    if EMAIL_FILTER_MODE == "whitelist":
        logger.info(f"  Whitelist:     {ONLY_REPLY_TO}")
    elif EMAIL_FILTER_MODE == "blocklist":
        logger.info(f"  Blocklist:     {IGNORE_SENDERS}")
    logger.info(f"  Poll interval: {POLL_INTERVAL_SECONDS}s")
    logger.info(f"  Label:         {LABEL_AFTER_REPLY or 'none'}")
    logger.info("=" * 55)

    service = get_gmail_service()
    seen_ids = set()

    while True:
        try:
            emails = get_unread_emails(service)
            new_emails = [e for e in emails if e["id"] not in seen_ids]

            if not new_emails:
                logger.debug(f"No new emails. Sleeping {POLL_INTERVAL_SECONDS}s...")
            else:
                logger.info(f"Found {len(new_emails)} new email(s).")

            for email in new_emails:
                seen_ids.add(email["id"])
                if should_process(email):
                    process_email(service, email)
                else:
                    logger.debug(f"Skipped: {email.get('sender', '?')} — {email.get('subject', '?')}")

        except KeyboardInterrupt:
            logger.info("Agent stopped by user (Ctrl+C).")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            logger.info(f"Retrying in {POLL_INTERVAL_SECONDS}s...")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_polling_loop()
