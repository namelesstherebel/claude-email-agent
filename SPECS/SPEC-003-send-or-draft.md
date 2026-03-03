# SPEC-003: Send or Draft Handler

> Version: 1.0.0 | Status: complete

---

## Purpose

After generating a reply, either save it as a Gmail draft or send it immediately, based on `REPLY_MODE`.

---

## Implementation

**File:** `agent.py` (routing) + `gmail_client.py` (Gmail API calls)

**Draft mode** (default):
- Creates a new draft in the user's Gmail account
- Draft is in the same thread as the original email
- User can review, edit, and send manually
- Subject is prefixed with `Re:` if not already

**Send mode** (opt-in):
- Sends the reply immediately via `users.messages.send`
- Same thread as the original email
- Cannot be undone — ensure prompt quality before enabling

**Post-processing (both modes):**
- Original email is marked as read (`UNREAD` label removed)
- Optional Gmail label applied (`LABEL_AFTER_REPLY` setting)

---

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `REPLY_MODE` | draft | Set to `send` to auto-send |
| `LABEL_AFTER_REPLY` | AI-Replied | Leave blank to skip labeling |

---

## Safety Notes

- **Always start in `draft` mode**. Review replies for several days before switching to `send`.
- The most common failure mode is an unexpected email type (a recruiter, a legal notice, an automated system) receiving an auto-generated reply.
- Sender whitelisting (`ONLY_REPLY_TO`) is strongly recommended when using `send` mode.
- Blocklist patterns (`IGNORE_SENDERS`) prevent replies to newsletters and auto-senders.
