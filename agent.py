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


def should_process(email):
    """
    Return True if this email should be processed.
    Applies sender whitelist and blocklist filters.
    """
    sender = email.get("sender", "").lower()

    # Whitelist: if set, only process senders on the list
    if ONLY_REPLY_TO:
        if not any(allowed.lower() in sender for allowed in ONLY_REPLY_TO):
            logger.debug(f"Skipping (not in whitelist): {sender}")
            return False

    # Blocklist: skip senders matching ignore patterns
    for pattern in IGNORE_SENDERS:
        if pattern.lower() in sender:
            logger.debug(f"Skipping (blocklist match '{pattern}'): {sender}")
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
        logger.error(f"Failed to generate reply: {e}")
        return

    if REPLY_MODE == "send":
        send_reply(service, reply_to, subject, reply_text, thread_id)
        logger.info(f"Reply SENT to {reply_to}")
    else:
        create_draft(service, reply_to, subject, reply_text, thread_id)
        logger.info(f"Draft CREATED for {reply_to}")

    # Mark original as read and apply tracking label
    mark_as_read(service, msg_id)
    if LABEL_AFTER_REPLY:
        apply_label(service, msg_id, LABEL_AFTER_REPLY)


def run_polling_loop():
    """
    Main polling loop. Runs indefinitely, checking for new emails every
    POLL_INTERVAL_SECONDS seconds.
    """
    logger.info("Starting Claude Email Agent...")
    logger.info(f"  Mode:            {REPLY_MODE.upper()}")
    logger.info(f"  Poll interval:   {POLL_INTERVAL_SECONDS}s")
    logger.info(f"  Sender filter:   {ONLY_REPLY_TO or 'all'}")
    logger.info(f"  Label on reply:  {LABEL_AFTER_REPLY or 'none'}")
    logger.info("-" * 50)

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

        except KeyboardInterrupt:
            logger.info("Agent stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in polling loop: {e}", exc_info=True)
            logger.info(f"Retrying in {POLL_INTERVAL_SECONDS}s...")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_polling_loop()
