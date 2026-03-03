"""
claude_agent.py
Claude API integration with prompt caching for email reply generation.
"""

import os
import logging
from anthropic import Anthropic

from config import SYSTEM_PROMPT, MODEL, MAX_TOKENS

logger = logging.getLogger(__name__)

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def generate_reply(email_subject, email_body, sender, thread_history=None):
    """
    Generate a reply to an email using Claude with prompt caching.

    Args:
        email_subject: Subject line of the incoming email
        email_body: Body text of the incoming email
        sender: Sender email/name string
        thread_history: Optional list of prior messages in the thread for context

    Returns:
        str: The generated reply text (body only, no subject line)
    """

    # Build the messages list
    messages = []

    # Include thread history for contextual replies
    if thread_history:
        for entry in thread_history:
            messages.append({
                "role": entry["role"],
                "content": entry["content"]
            })

    # Add the current email as the user message
    user_content = f"From: {sender}\nSubject: {email_subject}\n\n{email_body}"
    messages.append({
        "role": "user",
        "content": user_content
    })

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    # Prompt caching: the system prompt is cached after the first call.
                    # Subsequent calls within 5 minutes cost 90% less for this block.
                    # Requires the cached block to be >= 1,024 tokens.
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=messages
        )

        # Log cache usage for transparency
        usage = response.usage
        logger.debug(
            f"Tokens — input: {usage.input_tokens}, "
            f"cache_write: {getattr(usage, 'cache_creation_input_tokens', 0)}, "
            f"cache_read: {getattr(usage, 'cache_read_input_tokens', 0)}, "
            f"output: {usage.output_tokens}"
        )

        cache_read = getattr(usage, 'cache_read_input_tokens', 0)
        if cache_read > 0:
            logger.info(f"Prompt cache HIT — saved ~{cache_read} input tokens.")

        reply_text = response.content[0].text
        return reply_text.strip()

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise


def verify_caching():
    """
    Send two test messages to confirm prompt caching is working.
    Logs the cache token counts for both calls.
    Call this once after setup to verify your system prompt is large enough.
    """
    test_email = {
        "subject": "Test",
        "body": "Hello, this is a test email.",
        "sender": "test@example.com"
    }

    logger.info("--- Caching verification: Call 1 (expect cache_write > 0) ---")
    generate_reply(test_email["subject"], test_email["body"], test_email["sender"])

    logger.info("--- Caching verification: Call 2 (expect cache_read > 0) ---")
    generate_reply(test_email["subject"], test_email["body"], test_email["sender"])

    logger.info("If you see cache_read > 0 on Call 2, caching is working correctly.")
    logger.info("If cache_write = 0 on Call 1, your system prompt may be under 1,024 tokens.")
