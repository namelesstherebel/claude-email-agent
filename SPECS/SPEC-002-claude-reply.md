# SPEC-002: Claude Reply Generation

> Version: 1.0.0 | Status: complete

---

## Purpose

Generate a contextual, persona-appropriate email reply using the Claude API with prompt caching.

---

## Implementation

**File:** `claude_agent.py`

**API call structure:**
```
client.messages.create(
  model=MODEL,
  max_tokens=MAX_TOKENS,
  system=[{
    'type': 'text',
    'text': SYSTEM_PROMPT,
    'cache_control': {'type': 'ephemeral'}
  }],
  messages=[{
    'role': 'user',
    'content': 'From: {sender}\nSubject: {subject}\n\n{body}'
  }]
)
```

**Prompt caching:**
- The `cache_control: ephemeral` block caches the system prompt for 5 minutes
- Cache reads cost 10% of normal input price (90% savings)
- Minimum 1,024 tokens required for caching to activate
- Verify with: `usage.cache_read_input_tokens > 0` on the second call

---

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `MODEL` | claude-haiku-4-5 | Model to use for generation |
| `MAX_TOKENS` | 1024 | Max reply length in tokens |
| `SYSTEM_PROMPT` | (template) | **Must be customized** in config.py |

---

## Prompt Caching Verification

Run `verify_caching()` from `claude_agent.py` after setup:
```python
from claude_agent import verify_caching
verify_caching()
```

On Call 1: `cache_creation_input_tokens > 0` (prompt written to cache)
On Call 2: `cache_read_input_tokens > 0` (reading from cache — 90% discount active)

If `cache_write = 0` on Call 1, your system prompt is under 1,024 tokens.
Add more persona context, FAQs, or example replies to increase it.

---

## Thread Context (Optional)

Pass `thread_history` to include prior messages in the reply context:
```python
reply = generate_reply(
    subject, body, sender,
    thread_history=[
        {'role': 'user', 'content': prior_email},
        {'role': 'assistant', 'content': prior_reply}
    ]
)
```
