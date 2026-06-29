---
type: knowledge_index
title: Nano Banana Pro VIZIGROK Knowledge Index
tags:
  - nano-banana-pro
  - kie-ai
  - image-generation
  - automation
  - vizigrok
  - compaction
---

# Nano Banana Pro VIZIGROK Knowledge Index

## Routing rule

Do not scan the whole repository first. Route through:

1. `CLAUDE.md`
2. `compaction/VIZIGROK_COMPACTION.md`
3. `compaction/VIZIGROK_PACKET.yaml`
4. `skills/nano-banana-pro/SKILL.md`
5. `ledger/*.jsonl`

## Canonical flow

1. Build a prompt or prompt batch.
2. Submit to Kie.ai `createTask` with `model: nano-banana-pro`.
3. Receive a task ID.
4. Either poll `recordInfo` or receive a callback.
5. Extract result URLs.
6. Download immediately into durable storage.
7. Record metadata in SQLite.
8. Review, publish, archive, or re-run.

## VIZIGROK surfaces

- Markdown: rehydration and handoff.
- YAML/JSON: structured packet.
- JSONL: append-only trail.
- Mermaid: topology.
- HTML: visual cockpit.
- Source code: execution truth.

## Knowledge notes

- Kie.ai tasks are asynchronous.
- Callback mode is preferred for production.
- Polling mode is simplest for local testing.
- Provider media URLs may expire, so local archival is part of the automation, not an afterthought.
- The spoken provider name `Key.ai` remains an open ambiguity until confirmed.

## Open questions

- Where should final assets live: local disk, Google Drive, S3/R2, GitHub release, or another DAM?
- What should trigger jobs: CSV, Google Sheet, web form, folder watch, Slack command, or scheduled run?
- What review gate is required before publish?
