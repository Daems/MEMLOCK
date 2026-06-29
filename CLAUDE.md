# CLAUDE.md

This repository automates Nano Banana Pro image generation via Kie.ai and has been compacted into a **VIZIGROK rehydration packet**.

## Start here

Read in this order. Do not recursively spelunk the repo first.

1. `compaction/VIZIGROK_COMPACTION.md`
2. `compaction/VIZIGROK_PACKET.yaml`
3. `README.md`
4. `skills/nano-banana-pro/SKILL.md`
5. `okf/index.md`
6. `ledger/DECISIONS.jsonl`, `ledger/TASKS.jsonl`, `ledger/OPEN_QUESTIONS.jsonl`, `ledger/RISKS.jsonl`

## Operating rules

- Treat source files as truth before chat memory.
- Preserve the compaction trail. Append decisions/tasks/questions/risks to JSONL instead of overwriting history.
- Never commit `.env`, API keys, generated outputs, or private input images.
- Keep API credentials server-side only.
- Prefer callback mode for production and polling mode for local testing.
- Download generated outputs promptly and record task metadata in SQLite.
- No automatic publish without a human review gate.
- Add tests before refactoring the client or CLI.

## Safe defaults

- Default resolution: `1K`
- Default format: `png`
- Default aspect ratio: `1:1`
- Default model: `nano-banana-pro`

## VIZIGROK surface roles

- Markdown = anti-restart handoff.
- YAML/JSON = agent-ingestable packet.
- JSONL = append-only trail.
- Mermaid = topology.
- HTML = living cockpit, not source of truth.
- OKF = durable knowledge routing.
