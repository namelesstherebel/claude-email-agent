# SPEC_INVENTORY.md -- Specification Inventory

This file lists all feature specifications for the Claude Email Agent project.
Each spec lives in the SPECS/ folder and describes one feature in detail.

---

## Specifications

| ID | Title | Status | File |
|---|---|---|---|
| SPEC-001 | Gmail Polling via Gmail API | Complete | SPECS/SPEC-001-gmail-polling.md |
| SPEC-002 | Claude Reply Generation | Complete | SPECS/SPEC-002-claude-reply.md |
| SPEC-003 | Send or Draft Mode | Complete | SPECS/SPEC-003-send-or-draft.md |
| SPEC-004 | Email Filter Mode (Whitelist / Blocklist) | Complete | SPECS/SPEC-004-email-filter-mode.md |
| SPEC-005 | Multi-Provider Email Support | Complete | SPECS/SPEC-005-multi-provider.md |

---

## Status Definitions

- **Draft** -- written but not yet implemented
- **In Progress** -- currently being implemented
- **Complete** -- implemented and tested
- **Deprecated** -- no longer active

---

## Summary

SPEC-001 through SPEC-004 cover the core Gmail-based agent with filtering.
SPEC-005 extends the agent to support Outlook, Yahoo, iCloud, and any IMAP provider
without breaking the existing Gmail flow.
