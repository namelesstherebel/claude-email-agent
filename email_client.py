"""
email_client.py
Provider-agnostic email client abstraction.

All providers expose the same interface:
  get_unread()                                  -> list[dict]
  send_reply(to, subject, body, thread_id)      -> None
  create_draft(to, subject, body, thread_id)    -> None
  mark_read(msg_id)                             -> None

Each returned message dict contains:
  id, subject, sender, reply_to, body, thread_id, snippet

Usage (handled automatically by agent.py based on EMAIL_PROVIDER in .env):
  from email_client import GmailClient, OutlookClient, IMAPClient
"""

import os
import base64
import email as email_lib
import imaplib
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


# ─── Base Interface ───────────────────────────────────────────────────────────

class EmailClient:
    """
    Abstract base class. All providers must implement these four methods.
    agent.py only ever calls these — it never touches provider internals.
    """

    def get_unread(self) -> list:
        raise NotImplementedError

    def send_reply(self, to: str, subject: str, body: str, thread_id: str) -> None:
        raise NotImplementedError

    def create_draft(self, to: str, subject: str, body: str, thread_id: str) -> None:
        raise NotImplementedError

    def mark_read(self, msg_id: str) -> None:
        raise NotImplementedError

    def apply_label(self, msg_id: str, label_name: str) -> None:
        """Optional — providers that don't support labels can silently skip."""
        pass


# ─── Gmail Client (Google API + OAuth2) ──────────────────────────────────────

class GmailClient(EmailClient):
    """
    Wraps the existing gmail_client.py module.
    Zero changes to Gmail flow — existing users are unaffected.
    """

    def __init__(self):
        import gmail_client as _gc
        self._gc = _gc
        self._service = _gc.get_gmail_service()
        logger.info("GmailClient initialized via Google OAuth2.")

    def get_unread(self) -> list:
        return self._gc.get_unread_emails(self._service)

    def send_reply(self, to: str, subject: str, body: str, thread_id: str) -> None:
        self._gc.send_reply(self._service, to, subject, body, thread_id)

    def create_draft(self, to: str, subject: str, body: str, thread_id: str) -> None:
        self._gc.create_draft(self._service, to, subject, body, thread_id)

    def mark_read(self, msg_id: str) -> None:
        self._gc.mark_as_read(self._service, msg_id)

    def apply_label(self, msg_id: str, label_name: str) -> None:
        self._gc.apply_label(self._service, msg_id, label_name)


# ─── Outlook Client (Microsoft Graph API + MSAL) ─────────────────────────────

class OutlookClient(EmailClient):
    """
    Uses Microsoft Graph API via MSAL (OAuth2 client credentials flow).
    Requires in .env: OUTLOOK_CLIENT_ID, OUTLOOK_CLIENT_SECRET, OUTLOOK_TENANT_ID

    For personal outlook.com / hotmail.com accounts set OUTLOOK_TENANT_ID=consumers
    For work / school accounts use the tenant GUID from Azure.

    Graph API docs: https://learn.microsoft.com/en-us/graph/api/overview
    """

    GRAPH_BASE = "https://graph.microsoft.com/v1.0"
    SCOPES = ["https://graph.microsoft.com/.default"]

    def __init__(self):
        try:
            import msal
            import requests as _requests
        except ImportError:
            raise ImportError(
                "Outlook requires the 'msal' and 'requests' packages. "
                "Run: pip install msal requests"
            )

        self._requests = _requests

        client_id     = os.environ.get("OUTLOOK_CLIENT_ID", "")
        client_secret = os.environ.get("OUTLOOK_CLIENT_SECRET", "")
        tenant_id     = os.environ.get("OUTLOOK_TENANT_ID", "common")

        if not client_id or not client_secret:
            raise ValueError(
                "OUTLOOK_CLIENT_ID and OUTLOOK_CLIENT_SECRET must be set in .env"
            )

        authority = f"https://login.microsoftonline.com/{tenant_id}"
        self._app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )
        self._token = None
        self._refresh_token()
        logger.info("OutlookClient initialized via Microsoft Graph.")

    def _refresh_token(self):
        result = self._app.acquire_token_silent(self.SCOPES, account=None)
        if not result:
            result = self._app.acquire_token_for_client(scopes=self.SCOPES)
        if "access_token" not in result:
            raise RuntimeError(
                f"Could not acquire Microsoft Graph token: {result.get('error_description', result)}"
            )
        self._token = result["access_token"]

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict = None) -> dict:
        r = self._requests.get(
            f"{self.GRAPH_BASE}{path}", headers=self._headers(), params=params
        )
        if r.status_code == 401:
            self._refresh_token()
            r = self._requests.get(
                f"{self.GRAPH_BASE}{path}", headers=self._headers(), params=params
            )
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: dict) -> dict:
        r = self._requests.post(
            f"{self.GRAPH_BASE}{path}", headers=self._headers(), json=payload
        )
        if r.status_code == 401:
            self._refresh_token()
            r = self._requests.post(
                f"{self.GRAPH_BASE}{path}", headers=self._headers(), json=payload
            )
        r.raise_for_status()
        return r.json() if r.content else {}

    def _patch(self, path: str, payload: dict) -> None:
        r = self._requests.patch(
            f"{self.GRAPH_BASE}{path}", headers=self._headers(), json=payload
        )
        if r.status_code == 401:
            self._refresh_token()
            r = self._requests.patch(
                f"{self.GRAPH_BASE}{path}", headers=self._headers(), json=payload
            )
        r.raise_for_status()

    def get_unread(self) -> list:
        data = self._get(
            "/me/mailFolders/inbox/messages",
            params={"$filter": "isRead eq false", "$top": "50",
                    "$select": "id,subject,from,replyTo,body,conversationId,bodyPreview"}
        )
        messages = []
        for msg in data.get("value", []):
            sender_obj = msg.get("from", {}).get("emailAddress", {})
            sender = f"{sender_obj.get('name', '')} <{sender_obj.get('address', '')}>".strip()
            reply_tos = msg.get("replyTo", [])
            if reply_tos:
                rt = reply_tos[0].get("emailAddress", {})
                reply_to = f"{rt.get('name', '')} <{rt.get('address', '')}>".strip()
            else:
                reply_to = sender

            body_content = msg.get("body", {}).get("content", "")
            body_type    = msg.get("body", {}).get("contentType", "text")
            if body_type == "html":
                body_content = re.sub(r"<[^>]+>", " ", body_content).strip()

            messages.append({
                "id":        msg["id"],
                "thread_id": msg.get("conversationId", msg["id"]),
                "subject":   msg.get("subject", "(no subject)"),
                "sender":    sender,
                "reply_to":  reply_to,
                "body":      body_content,
                "snippet":   msg.get("bodyPreview", ""),
            })
        return messages

    def send_reply(self, to: str, subject: str, body: str, thread_id: str) -> None:
        subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        self._post("/me/sendMail", {
            "message": {
                "subject": subj,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": to}}],
            },
            "saveToSentItems": True,
        })
        logger.info(f"Outlook reply sent to {to}")

    def create_draft(self, to: str, subject: str, body: str, thread_id: str) -> None:
        subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        draft = self._post("/me/messages", {
            "subject": subj,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": to}}],
        })
        logger.info(f"Outlook draft created (id: {draft.get('id', '?')})")

    def mark_read(self, msg_id: str) -> None:
        self._patch(f"/me/messages/{msg_id}", {"isRead": True})

    # apply_label: Outlook uses categories instead of labels — optional enhancement


# ─── IMAP Client (Yahoo, iCloud, Zoho, Fastmail, custom) ─────────────────────

class IMAPClient(EmailClient):
    """
    Generic IMAP/SMTP client using Python stdlib only.
    Works for Yahoo Mail, iCloud Mail, and any IMAP/SMTP provider.

    Requires in .env:
      EMAIL_ADDRESS      — your full email address
      EMAIL_APP_PASSWORD — app password (NOT your main login password)
      IMAP_HOST          — e.g. imap.mail.yahoo.com
      IMAP_PORT          — default 993
      SMTP_HOST          — e.g. smtp.mail.yahoo.com
      SMTP_PORT          — default 587
    """

    def __init__(self):
        self._address  = os.environ.get("EMAIL_ADDRESS", "")
        self._password = os.environ.get("EMAIL_APP_PASSWORD", "")
        self._imap_host = os.environ.get("IMAP_HOST", "")
        self._imap_port = int(os.environ.get("IMAP_PORT", "993"))
        self._smtp_host = os.environ.get("SMTP_HOST", "")
        self._smtp_port = int(os.environ.get("SMTP_PORT", "587"))

        missing = [k for k, v in {
            "EMAIL_ADDRESS": self._address,
            "EMAIL_APP_PASSWORD": self._password,
            "IMAP_HOST": self._imap_host,
            "SMTP_HOST": self._smtp_host,
        }.items() if not v]
        if missing:
            raise ValueError(
                f"Missing required .env variables for IMAP client: {', '.join(missing)}"
            )

        logger.info(f"IMAPClient initialized for {self._address} via {self._imap_host}")

    def _connect_imap(self):
        """Open an SSL IMAP connection and log in."""
        conn = imaplib.IMAP4_SSL(self._imap_host, self._imap_port)
        conn.login(self._address, self._password)
        return conn

    def get_unread(self) -> list:
        messages = []
        conn = self._connect_imap()
        try:
            conn.select("INBOX")
            _, data = conn.search(None, "UNSEEN")
            msg_ids = data[0].split()
            for uid in msg_ids[-50:]:  # cap at 50
                _, msg_data = conn.fetch(uid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email_lib.message_from_bytes(raw)

                subject = self._decode_header(msg.get("Subject", "(no subject)"))
                sender  = msg.get("From", "")
                reply_to = msg.get("Reply-To", sender)
                body    = self._extract_body(msg)

                # Skip auto-generated
                if msg.get("List-Unsubscribe") or msg.get("Auto-Submitted", "no") != "no":
                    continue

                messages.append({
                    "id":        uid.decode(),
                    "thread_id": msg.get("Message-ID", uid.decode()),
                    "subject":   subject,
                    "sender":    sender,
                    "reply_to":  reply_to,
                    "body":      body,
                    "snippet":   body[:200],
                })
        finally:
            conn.logout()
        return messages

    @staticmethod
    def _decode_header(value: str) -> str:
        """Decode potentially encoded email header values."""
        parts = email_lib.header.decode_header(value)
        decoded = []
        for part, charset in parts:
            if isinstance(part, bytes):
                decoded.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                decoded.append(part)
        return " ".join(decoded)

    @staticmethod
    def _extract_body(msg) -> str:
        """Extract plain text body from a MIME message."""
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                cd = str(part.get("Content-Disposition", ""))
                if ct == "text/plain" and "attachment" not in cd:
                    charset = part.get_content_charset() or "utf-8"
                    return part.get_payload(decode=True).decode(charset, errors="replace")
            # Fallback to HTML part
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    charset = part.get_content_charset() or "utf-8"
                    html = part.get_payload(decode=True).decode(charset, errors="replace")
                    return re.sub(r"<[^>]+>", " ", html).strip()
        else:
            charset = msg.get_content_charset() or "utf-8"
            return msg.get_payload(decode=True).decode(charset, errors="replace")
        return ""

    def _send_via_smtp(self, to: str, subject: str, body: str) -> None:
        """Send an email via SMTP with STARTTLS."""
        msg = MIMEMultipart()
        msg["From"]    = self._address
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self._smtp_host, self._smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self._address, self._password)
            smtp.sendmail(self._address, to, msg.as_string())

    def send_reply(self, to: str, subject: str, body: str, thread_id: str) -> None:
        subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        self._send_via_smtp(to, subj, body)
        logger.info(f"IMAP reply sent to {to}")

    def create_draft(self, to: str, subject: str, body: str, thread_id: str) -> None:
        """Append a message to the Drafts folder via IMAP APPEND."""
        subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        msg = MIMEText(body)
        msg["From"]    = self._address
        msg["To"]      = to
        msg["Subject"] = subj

        conn = self._connect_imap()
        try:
            # Common Drafts folder names across providers
            draft_folders = ["Drafts", "Draft", "[Gmail]/Drafts", "INBOX.Drafts"]
            appended = False
            for folder in draft_folders:
                try:
                    conn.append(
                        folder,
                        "\Draft",
                        imaplib.Time2Internaldate(None),
                        msg.as_bytes()
                    )
                    logger.info(f"IMAP draft appended to {folder}")
                    appended = True
                    break
                except Exception:
                    continue
            if not appended:
                logger.warning(
                    "Could not find Drafts folder. Falling back to sending the reply directly."
                )
                self._send_via_smtp(to, subj, body)
        finally:
            conn.logout()

    def mark_read(self, msg_id: str) -> None:
        """Mark a message as seen via IMAP STORE."""
        conn = self._connect_imap()
        try:
            conn.select("INBOX")
            conn.store(msg_id, "+FLAGS", "\Seen")
        finally:
            conn.logout()
