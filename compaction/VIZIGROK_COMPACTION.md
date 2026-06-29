---
type: vizigrok_compaction
id: vizigrok.nano-banana-pro.v0.1
project: Nano Banana Pro Automation
status: rehydrate_ready
created_utc: 2026-06-29T16:45:00Z
source_provider: Kie.ai Nano Banana Pro API
truth_hierarchy:
  - repo_source_files
  - compaction_packet
  - okf_pages
  - ledger_jsonl
  - prior_chat_context
routing_files:
  - CLAUDE.md
  - okf/index.md
  - compaction/VIZIGROK_PACKET.yaml
  - dashboards/vizigrok_compaction.html
---

# VIZIGROK Compaction · Nano Banana Pro Automation

## Core thesis

This repo is no longer just a tiny Nano Banana Pro CLI. It is a **VIZIGROK compaction packet**: a compressed, model-agnostic handoff that lets a coding agent rehydrate the project, understand the workflow, preserve decisions, and extend the automation without restarting from chat fog.

> The answer is not the primary object. The trail is.

## What this artifact preserves

- **Operational code** for Kie.ai Nano Banana Pro task creation, polling, callbacks, downloads, and SQLite task logging.
- **Agent routing** through `CLAUDE.md`, `okf/index.md`, and `skills/nano-banana-pro/SKILL.md`.
- **Compaction packet** in Markdown, YAML, JSON, Mermaid, HTML, and append-only JSONL.
- **Anti-restart posture**: a future agent should read the packet and continue, not regenerate the scaffold from scratch.

## Current implementation snapshot

| Layer | Current state |
|---|---|
| Provider | Kie.ai API for `nano-banana-pro` |
| Interface | Python CLI and FastAPI callback receiver |
| Inputs | Direct prompt, YAML job, CSV batch |
| Outputs | Downloaded media into `outputs/` |
| Memory | SQLite task log |
| Agent instructions | `CLAUDE.md` plus `SKILL.md` |
| Knowledge format | OKF-flavored Markdown pages |
| VIZIGROK surface | `dashboards/vizigrok_compaction.html` |

## Canonical workflow

```text
prompt/source queue
  → validate job
  → submit Kie.ai createTask
  → persist task id
  → callback or poll recordInfo
  → extract result URLs
  → download output immediately
  → log metadata in SQLite
  → review/publish/archive
```

## Rehydration order

A coding agent should read files in this order:

1. `CLAUDE.md`
2. `compaction/VIZIGROK_COMPACTION.md`
3. `compaction/VIZIGROK_PACKET.yaml`
4. `README.md`
5. `skills/nano-banana-pro/SKILL.md`
6. `src/nb_auto/kie_client.py`
7. `src/nb_auto/cli.py`
8. `src/nb_auto/storage.py`
9. `src/nb_auto/callback_server.py`
10. `ledger/*.jsonl`

## Control grammar

```yaml
vizigrok_control:
  mode: "compaction"
  doctrine:
    - "route before search"
    - "code before chat memory"
    - "append decisions, do not overwrite history"
    - "HTML is cockpit, not truth ledger"
    - "Mermaid is topology"
    - "JSONL is evidence trail"
    - "OKF is durable knowledge map"
  invocation:
    symbol: "- <>UCC/UV ¿?"
    read_as: "activate bidirectional concept channel with uncertainty-vector question gate"
```

## Immediate next build moves

1. Add tests for payload construction, response decoding, URL extraction, and SQLite logging.
2. Add a dry-run mode that prints the API payload without sending it.
3. Add job manifests so each generated asset has source prompt, model, provider task id, and local path.
4. Add a review queue: `queued → submitted → completed → reviewed → published → archived`.
5. Add optional Google Drive/S3/R2 storage target after local output is stable.
6. Add provider callback signature verification if Kie provides a signing method.

## Open questions for Jeffrey

- Did “Key.ai” mean **Kie.ai**, or should a second provider adapter be created?
- Should the first real trigger be CSV, Google Sheet, folder watch, Slack command, or web form?
- Should final images live locally only, or also in Drive/S3/R2/GitHub?
- Should this stay image-generation-only, or become a broader generative media queue?
- Default output level: `1K` for cheap drafts, `2K` for review, or `4K` only for finals?

## Non-goals for this compaction

- Do not expose API keys in HTML or browser code.
- Do not treat generated output URLs as durable storage.
- Do not replace source files with the HTML dashboard.
- Do not publish generated assets automatically without a review gate.
