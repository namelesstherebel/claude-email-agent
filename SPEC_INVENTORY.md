# SPEC_INVENTORY.md — Task Inventory and Spec Queue

> Version: 1.0.0 | Last updated: initialized

---

## Spec Status

| Spec ID | Name | Status | File |
|---|---|---|---|
| SPEC-001 | Gmail Polling Loop | complete | SPECS/SPEC-001-gmail-polling.md |
| SPEC-002 | Claude Reply Generation | complete | SPECS/SPEC-002-claude-reply.md |
| SPEC-003 | Send or Draft Handler | complete | SPECS/SPEC-003-send-or-draft.md |
| SPEC-004 | Persona Configuration | pending | SPECS/SPEC-004-persona-config.md |
| SPEC-005 | Deployment Setup | pending | SPECS/SPEC-005-deployment.md |

---

## Spec Queue (Pending)

The following specs are queued for the onboarding workflow to complete:

**SPEC-004: Persona Configuration**
Define the specific persona, tone, and reply rules for this deployment.
Blocked on: user completing `*onboard` Phase 2 (Context Engineering)

**SPEC-005: Deployment Setup**
Document the specific deployment configuration (local vs server, service file, Docker).
Blocked on: user completing `*onboard` Phase 5 (Environment Build)

---

## Adding New Specs

When extending the agent (e.g., adding Pub/Sub, calendar integration, thread context):
1. Create a new spec in `SPECS/` following the existing format
2. Add it to the inventory table above
3. Run `*reflect` to generate improvement proposals if relevant
