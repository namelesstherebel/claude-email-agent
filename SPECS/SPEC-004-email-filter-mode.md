# SPEC-004: Email Filter Mode

> Version: 1.0.0 | Status: complete

---

## Purpose

Control precisely which emails the agent responds to — from maximum safety (specific people only) to fully open (reply to all).

---

## Three Modes

### whitelist — Only reply to specific people

The agent only responds if the sender matches at least one entry in `ONLY_REPLY_TO`.
Matching is case-insensitive and uses substring matching — so `@company.com` matches any sender from that domain.

**When to use:**
- Starting out for the first time
- Using auto-send mode
- Responding only to known contacts (team, clients, partners)

**Configuration:**
```
EMAIL_FILTER_MODE=whitelist
ONLY_REPLY_TO=alice@company.com, bob@company.com, @trustedcorp.com
```

**Safety layer:** Even in whitelist mode, the blocklist is still applied. If a whitelisted sender somehow matches a blocklist pattern, the email is still skipped.

---

### blocklist — Reply to everyone except blocked senders

The agent responds to all emails except those where the sender matches a pattern in `IGNORE_SENDERS`.

**When to use:**
- Customer support or public-facing inboxes
- When you need broad coverage but still want to skip newsletters/spam

**Configuration:**
```
EMAIL_FILTER_MODE=blocklist
IGNORE_SENDERS=noreply@,no-reply@,mailer-daemon@,newsletter@
```

**Note:** Even emails that pass the blocklist check are still filtered by Gmail-level signals — emails with `List-Unsubscribe` headers and `Auto-Submitted` headers are always skipped (handled in `gmail_client.py`).

---

### all — No filter

The agent responds to every email. The blocklist is NOT applied in this mode (except as a minimum safety layer for system-level senders).

**When to use:**
- Rarely. Only if you have high confidence in your setup and system prompt.

**Safety block:** The pre-flight check in `agent.py` will refuse to start if `EMAIL_FILTER_MODE=all` AND `REPLY_MODE=send`. You must use `draft` mode with the `all` filter.

---

## Implementation

**File:** `agent.py` — `should_process()` function
**Config:** `config.py` — `EMAIL_FILTER_MODE`, `ONLY_REPLY_TO`, `IGNORE_SENDERS`
**Safety:** `agent.py` — `preflight_safety_check()` blocks unsafe combinations on startup

---

## Pre-Flight Safety Rules

| Combination | Result |
|---|---|
| `whitelist` + empty `ONLY_REPLY_TO` | Blocked (agent won't start) |
| `all` + `REPLY_MODE=send` | Blocked (agent won't start) |
| `blocklist` + `REPLY_MODE=send` | Allowed, but warning logged |
| `whitelist` + `REPLY_MODE=send` | Allowed (safest auto-send setup) |
