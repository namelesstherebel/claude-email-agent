# namelesstherebel/claude-email-agent

Read CLAUDE.md and preserve its rules; this file adds to them and does not replace them.

Provenance: https://github.com/namelesstherebel/saddle/blob/45fe8c4aa2b3deb644c5baa18980c80c67848b85/templates/AGENTS.md

Adoption snapshot base_sha40: `aac1f8b70e87b98dc94bc0df2cd278be84b25c65`. Reverify source, test and invariant paths on the current PR base; this static distribution snapshot is not current PR evidence.

## Review and validation

This repository is participating in the approved staged Pullfrog migration. Automatic Pullfrog supplies current-head expert review, including security. Until the owner verifies staged-cutover readiness, preserve existing review assignments and automatic-review settings. After readiness is verified, Pullfrog is the normal automatic reviewer and GitHub Reviewer is a manual fallback when needed, not a mandatory second review. Assess valid existing legacy findings; a provider name or skipped review is not evidence of coverage.

Once Mac Ops verifies successful current-head `pullfrog-approval` emission from Pullfrog app `1768019` and reads back the required rule, normal merge requires a fresh successful verdict from that app on the current head. The `pullfrog` workflow/job name alone is not that verdict; never assume or require an unverified, never-emitted check. Preserve all other applicable checks and safety, visual, release and owner-acceptance gates. Do not bypass protections or change settings under these instructions.

The current branch writer handles material findings, inspects corrections, verifies applicable source/secret checks and actual resulting-head CI, then performs a normal merge pinned to the reviewed head. Report missing, skipped, errored and non-applicable checks accurately. Source scanning is not dependency-advisory coverage; saved configuration is not proof of live review or successful provider operation.

Preserve Cubic integration, reviews and checks entirely. Retain independent Codex security review as complementary coverage; do not narrow Pullfrog's security lenses or remove security checks as duplicates. Shared expert prompts and provider settings are maintained separately, not copied or changed here.

Pullfrog fixes are opt-in, bounded handoffs only. The sole writer must explicitly hand off a contained correction and pause their own branch edits, inspect the returned diff, then obtain resulting-head CI and fresh review before normal merge. No blanket or unattended autofix is authorized; product and larger changes retain their assigned implementation owner.

## Review context

Context to cite, never invent: base SHA the current PR base SHA, obtained from GitHub for this review and cited explicitly (not the inventory snapshot SHA); invariant docs `CLAUDE.md`, `README.md`. Source paths: `agent.py`, `claude_agent.py`, `config.py`, `email_client.py`, `gmail_client.py`, `setup.sh`. Test paths: unavailable (no test paths found; no tests executed or claimed).

Assess actual coverage gaps rather than requiring test-file changes mechanically. Preserve the safety rules in CLAUDE.md; this migration does not authorize starting an agent, reading mail, sending replies, setup or deployment.

Labels (apply those whose criteria match):

- `frontend`: user-facing UI or client behavior changes.
- `backend`: server, service or API behavior changes.
- `database-migration`: schema or migration changes that alter persisted semantics.
- `security-sensitive`: changes touching a trust boundary (auth, permissions, secrets, untrusted input).
- `high-risk-architecture`: cross-module contracts or concurrency changes.
- `no-tests`: an unaddressed applicable test coverage gap.
