# Cloudflare Control Plane / Director Mesh

@ IF_YOU_ARE_AN_AI_OR_NEW_READER: READ THIS FIRST

- This project uses small docs. Do not put structure, runtime, policy, and decisions into one file.
- Start with `docs/derived/01_overview.md`.
 - If you need execution behavior, open `docs/derived/02_runtime_boundary.md`.
- If you nee policy or non-negotiable rules, open `docs/derived/03_guardrail.md`.
- If you need the reason for a key decision, open `docs/adr/adr_001_event_driven_control.md`.
 - Do not start with `docs/source/`. That folder is traceability input, not the working entry point.

- No doc should be big. One file = one responsibility.
- Every doc must say what it is for, what it updates, what it references, and what it must NOT contain.

## Purpose
This folder documents a Cloudflare-based control plane that coordinates agent delivery work while keeping GitHub as the source of truth for real artifacts.

## Quick navigation
- System shape: `docs/derived/01_overview.md`
- Runtime boundaries: `docs/derived/02_runtime_boundary.md`
- Guardrails: `docs/derived/03_guardrail.md`
- Decision record: `docs/adr/adr_001_event_driven_control.md`
- Machine-readable index: `registry/doc_index.json`
- Original sources: `docs/source/00_SOURCE_INDEX.md`

## Document writing rules

- One file = one role.
- Start with the most important information first.
 - Use short sections. Keep them scannable.
- Link to siblings instead of duplicating details.
- Add an `"What this file does not cover` section in every working doc.
- Keep ADRs immutable; supersede instead of editing.
