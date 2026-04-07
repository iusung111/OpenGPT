# 00_design_baseline

## Purpose
This file is the root-folder baseline for external CLI or non-ChatGPT workflows.
Start with this file before reading runtime or detail docs.

## Canonical source
- This file is a root-folder consumer copy of the current baseline intent.
- Canonical working source: `docs/derived/00_session_refined.md`
- Raw source: `docs/source/session_transcript_visible_chat_detailed.md`

## Core goals
- Build a Cloudflare-based control plane for autonomous software delivery
- Keep Cloudflare as metadata control, not real artifact storage
- Keep GitHub as the single source of truth for real artifacts
- Enforce event-driven processing, strict authority, and guardrails

## Non-negotiable rules
- All state changes are events
- Event log is append-only
- No multi-writer on the same resource
- Live deploy requires explicit user command
- All actions must pass through Mission Kernel

## System shape
- Control Plane: program director, release gate, quality/hygiene, session broker, kernel
- Agent Runtime: delivery pod, reliability pod
- Execution Plane: GitHub, verify, browser, deploy
- Artifact Plane: docs, registry, path index

## CLI start order
- 1. `README.md`
- 2. `00_design_baseline.md`
- 3. `01_current_progress.md`
- 4. `docs/derived/01_overview.md`
- 5. `runtime/` files

## What this file does not cover
- Full raw transcript
- Implementation details
- API or runtime specs
