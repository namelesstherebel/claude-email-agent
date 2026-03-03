# SPEC-001: Gmail Polling Loop

> Version: 1.0.0 | Status: complete

---

## Purpose

Poll Gmail for new unread emails at regular intervals and pass them to the Claude reply generator.

---

## Implementation

**File:** `agent.py` (main loop) + `gmail_client.py` (Gmail API helpers)

**Polling logic:**
1. Call `get_unread_emails(service)` which fetches messages with `labelIds=['INBOX', 'UNREAD']`
2. Compare returned message IDs against `seen_ids` set to detect new messages
3. For each new message, call `process_email(service, email)`
4. Sleep `POLL_INTERVAL_SECONDS` between polls

**Email parsing:**
- Extract `Subject`, `From`, `Reply-To` from headers
- Skip emails with `List-Unsubscribe` or `Auto-Submitted` headers (newsletters/auto-replies)
- Recursively extract `text/plain` body from MIME tree (falls back to HTML stripped of tags)

---

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `POLL_INTERVAL_SECONDS` | 60 | How often to check |
| `ONLY_REPLY_TO` | (empty) | Sender whitelist |
| `IGNORE_SENDERS` | noreply@,no-reply@,... | Sender blocklist |

---

## Edge Cases

- **OAuth expiry**: `token.json` auto-refreshes via `google-auth` library
- **API errors**: Caught with `try/except`, logged, loop continues
- **Large inboxes**: `maxResults=50` cap prevents excessive API calls
- **Duplicate processing**: `seen_ids` set prevents re-processing on next poll

---

## Future Upgrade

Replace polling with Gmail Push Notifications via Google Cloud Pub/Sub for real-time delivery.
See research doc in `CONTEXT/email-agent-research.md` for implementation guide.
