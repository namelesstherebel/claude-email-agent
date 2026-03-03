# SPEC-005: Multi-Provider Email Support

**Status:** Complete
**Implemented in:** email_client.py, agent.py, setup.sh, .env.example
**Added:** Round 3

---

## Goal

Allow the Claude Email Agent to work with any major email provider,
not just Gmail. The user picks their provider during setup and the
agent configures itself automatically.

---

## Supported Providers

| Provider | Auth | Implementation |
|---|---|---|
| Gmail | Google OAuth2 (credentials.json) | GmailClient (wraps gmail_client.py) |
| Outlook / Microsoft 365 | Azure MSAL | OutlookClient (Microsoft Graph API) |
| Yahoo Mail | App password + IMAP | IMAPClient |
| iCloud Mail | App-specific password + IMAP | IMAPClient |
| Any IMAP provider | App password + IMAP | IMAPClient |

---

## Architecture

### Base Interface (email_client.py)

All providers implement the same four methods:

- get_unread() -> list of dicts with {id, subject, sender, body, thread_id}
- send_reply(to, subject, body, thread_id) -> None -- sends reply immediately
- create_draft(to, subject, body, thread_id) -> None -- saves to Drafts folder
- mark_read(msg_id) -> None -- marks message as read

### GmailClient

Thin wrapper around the existing gmail_client.py module.
Preserves all existing Gmail OAuth2 behavior with zero changes.

### OutlookClient

Uses Microsoft Authentication Library (msal) for OAuth2.
Calls Microsoft Graph API REST endpoints for reading and sending email.

### IMAPClient

Uses Python stdlib imaplib and smtplib.
Connects to any IMAP server using credentials from .env.
Compatible with Yahoo, iCloud, Zoho, Fastmail, ProtonMail Bridge, and others.

---

## Setup Flow

setup.sh presents a numbered menu at Step 1 of 9:

1) Gmail (Google account)
2) Outlook / Microsoft 365 (work or personal)
3) Yahoo Mail
4) iCloud Mail (Apple)
5) Other / Custom (any IMAP provider)

Based on selection, setup.sh displays provider-specific credential instructions
and writes EMAIL_PROVIDER plus provider-specific variables to .env.

---

## Environment Variables

All providers require EMAIL_PROVIDER and ANTHROPIC_API_KEY.

Gmail additionally requires credentials.json in project folder.

Outlook additionally requires OUTLOOK_CLIENT_ID, OUTLOOK_CLIENT_SECRET,
and OUTLOOK_TENANT_ID (use 'consumers' for personal outlook.com accounts).

IMAP providers require EMAIL_ADDRESS, EMAIL_APP_PASSWORD,
IMAP_HOST, IMAP_PORT (default 993), SMTP_HOST, SMTP_PORT (default 587).

---

## Constraints

- The existing Gmail flow must not change -- GmailClient is a transparent wrapper
- All credentials stay in .env -- no new config files
- Each client is self-contained in email_client.py
- setup.sh branching is clean if/elif shell logic within one script
- Draft-first defaults and safety checks apply to all providers equally

---

## Dependencies Added

- msal (Microsoft OAuth2 for Outlook)
- requests (Microsoft Graph API calls)
- imaplib and smtplib are Python stdlib -- no install needed
