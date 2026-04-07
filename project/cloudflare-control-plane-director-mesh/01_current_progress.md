# 01_current_progress

## Purpose
This file summarizes the current implementation state for external CLI and offline work.
Read this after `00_design_baseline.md`.

## Current status
- Baseline docs and entry rules are in place
- Session-log-refined intent doc is in place
- Runtime skeletons have been created
- No GitHub-backed runtime adapter exists yet

## Created docs
- `README.md`
- `00_design_baseline.md`
- `01_current_progress.md`
- `docs/derived/00_session_refined.md`
- `docs/derived/01_overview.md`
- `docs/derived/02_runtime_boundary.md`
- `docs/derived/03_guardrail.md`
- `docs/derived/04_runtime_to_code_map.md`
- `docs/adr/adr_001_event_driven_control.md`
- `docs/adr/adr_002_github_truth.md`

## Created runtime files
- `runtime/kernel.ts`
- `runtime/session.ts`
- `runtime/queue.ts`
- `runtime/guardrail.ts`
- `runtime/executor.ts`
- `runtime/store.ts`

## Next external CLI tasks
- Implement a GitHub-backed store adapter
- Wire kernel + session + queue + guardrail + executor
- Add project-index or runtime bootstrap entry point
- Define event schema and lease persistence format

## Working rules
- Treat `00_design_baseline.md` as the root intent summary for CLI work
- Use `docs/derived/00_session_refined.md` for fuller baseline context
- Do not introduce live-deploy behaviour without explicit user command
