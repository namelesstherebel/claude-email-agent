# Email Agent Research

> Reference document for claude-email-agent design decisions.
> Always loaded by the agent for context.

---

## Architecture Overview

Three-layer design:
- **Layer 1** — Gmail API (OAuth2, polling or Pub/Sub)
- **Layer 2** — Claude API (prompt caching, model selection)
- **Layer 3** — Send or Draft (Gmail API write operations)

---

## Gmail API

**Authentication:** OAuth 2.0 (not username/password).
Required setup: Google Cloud Project, Gmail API enabled, OAuth credentials downloaded as `credentials.json`.

**Required scope:** `https://www.googleapis.com/auth/gmail.modify`
Allows: read, send, create drafts, add labels, mark as read.

**Polling approach:**
- `users.messages.list` with `labelIds=['INBOX', 'UNREAD']`
- Cost: 5 quota units per call (daily limit: 1 billion units)
- Simple, no infrastructure needed
- Polling interval: 60 seconds recommended

**Pub/Sub approach (production upgrade):**
- Gmail pushes notifications instantly via Google Cloud Pub/Sub
- Zero polling overhead
- Requires: Pub/Sub topic, webhook endpoint, `watch()` registration (expires every 7 days)
- Architecture: Gmail -> Pub/Sub -> Your server -> Claude -> Reply

---

## Claude API — Prompt Caching

**How it works:**
- Add `cache_control: {type: ephemeral}` to the system prompt block
- First call: pays full price to write prompt to cache (cache_creation_input_tokens > 0)
- Subsequent calls within 5 minutes: reads from cache at 10% of input price (cache_read_input_tokens > 0)
- Cache window resets on each use

**Minimum size:** 1,024 tokens for caching to activate.

**Verification:**
```python
usage = response.usage
print(usage.cache_creation_input_tokens)  # > 0 on first call
print(usage.cache_read_input_tokens)       # > 0 on subsequent calls
```

---

## Model Comparison

| Model | Speed | Input | Output | Best For |
|---|---|---|---|---|
| claude-haiku-4-5 | Fastest | $1/MTok | $5/MTok | Routine replies at volume |
| claude-sonnet-4-6 | Medium | $3/MTok | $15/MTok | Nuanced/complex emails |
| claude-opus-4-6 | Slowest | $5/MTok | $25/MTok | High-stakes replies |

**Recommendation:** claude-haiku-4-5 with prompt caching.

---

## Cost Analysis (100 emails/day)

Assumptions: ~600 token system prompt, ~200 token email, ~300 token reply.

| Scenario | Monthly Cost |
|---|---|
| No caching (haiku) | ~$6.90 |
| With caching (haiku) | ~$4.80 |
| 2,000 token prompt, no cache | ~$18.00 |
| 2,000 token prompt, with cache | ~$6.00 |

Prompt caching savings grow significantly with larger, more detailed system prompts.
A full FAQ + policy document baked into the system prompt is nearly free after the first call.

---

## Safety Checklist

- [ ] Test with a dedicated test Gmail account, not your main inbox
- [ ] Start in `REPLY_MODE=draft` — never auto-send first
- [ ] Add sender whitelist (`ONLY_REPLY_TO`) before enabling auto-send
- [ ] Skip newsletters: check for `List-Unsubscribe` headers
- [ ] Store API keys in `.env` — never hardcode
- [ ] Add `token.json` and `credentials.json` to `.gitignore`
- [ ] Verify caching: `usage.cache_read_input_tokens > 0` on second call

---

## Recommended Learning Path

1. Gmail API Python Quickstart — get OAuth working, read one email
2. Write a polling loop with print statements (no AI yet)
3. Add Anthropic SDK — test `generate_reply()` on a hardcoded email, verify caching
4. Wire it together in draft mode
5. Add filters, error handling, logging
6. Optionally: upgrade to Pub/Sub push notifications for production
