"""
gmail_client.py
Gmail API authentication, email reading, drafting, and sending helpers.
"""

import os
import base64
import logging
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# OAuth scopes — gmail.modify allows read + send + label
# Adjust if you only need read-only or draft-only access
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    """
    Authenticate with Gmail via OAuth2 and return an authorized service object.
    On first run, opens a browser window for user consent and saves token.json.
    On subsequent runs, loads token.json and auto-refreshes if expired.
    """
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    logger.info("Gmail service initialized.")
    return service


def get_unread_emails(service):
    """
    Returns a list of unread message dicts from INBOX.
    Each dict has: id, threadId, subject, sender, body, snippet.
    """
    try:
        result = service.users().messages().list(
            userId="me",
            labelIds=["INBOX", "UNREAD"],
            maxResults=50
        ).execute()
    except Exception as e:
        logger.error(f"Failed to list messages: {e}")
        return []

    messages = result.get("messages", [])
    emails = []
    for msg in messages:
        parsed = _parse_email(service, msg["id"])
        if parsed:
            emails.append(parsed)
    return emails


def _parse_email(service, msg_id):
    """Fetch and parse a single email into a clean dict."""
    try:
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()
    except Exception as e:
        logger.error(f"Failed to fetch message {msg_id}: {e}")
        return None

    headers = msg["payload"].get("headers", [])
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "")
    reply_to = next((h["value"] for h in headers if h["name"] == "Reply-To"), sender)

    # Skip auto-generated emails (newsletters, out-of-office, etc.)
    list_unsub = next((h["value"] for h in headers if h["name"] == "List-Unsubscribe"), None)
    auto_submitted = next((h["value"] for h in headers if h["name"] == "Auto-Submitted"), None)
    if list_unsub or (auto_submitted and auto_submitted != "no"):
        logger.debug(f"Skipping auto-generated email: {subject}")
        return None

    body = _extract_body(msg["payload"])

    return {
        "id": msg_id,
        "threadId": msg["threadId"],
        "subject": subject,
        "sender": sender,
        "reply_to": reply_to,
        "body": body,
        "snippet": msg.get("snippet", ""),
        "labelIds": msg.get("labelIds", []),
    }


def _extract_body(payload):
    """Recursively extract plain text body from a MIME payload."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    if mime_type == "text/html":
        # Fallback: use HTML body only if no plain text found at parent level
        data = payload.get("body", {}).get("data", "")
        if data:
            raw = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            # Strip HTML tags naively — good enough for context
            import re
            return re.sub(r"<[^>]+>", " ", raw).strip()

    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result

    return ""


def create_draft(service, to, subject, body, thread_id):
    """Save a reply as a Gmail draft (does NOT send it)."""
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw, "threadId": thread_id}}
    ).execute()

    logger.info(f"Draft created for thread {thread_id} (draft id: {draft['id']})")
    return draft


def send_reply(service, to, subject, body, thread_id):
    """Send a reply email immediately."""
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(
        userId="me",
        body={"raw": raw, "threadId": thread_id}
    ).execute()

    logger.info(f"Reply sent for thread {thread_id} (message id: {sent['id']})")
    return sent


def mark_as_read(service, msg_id):
    """Remove the UNREAD label from a message."""
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()


def apply_label(service, msg_id, label_name):
    """
    Apply a label to a message by name.
    Creates the label if it doesn't exist.
    """
    label_id = _get_or_create_label(service, label_name)
    if label_id:
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"addLabelIds": [label_id]}
        ).execute()


def _get_or_create_label(service, name):
    """Return the label ID for a given name, creating it if necessary."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"] == name:
            return label["id"]

    # Create new label
    new_label = service.users().labels().create(
        userId="me",
        body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
    ).execute()
    logger.info(f"Created Gmail label: {name}")
    return new_label["id"]
