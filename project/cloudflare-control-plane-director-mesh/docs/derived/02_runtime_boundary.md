# 02_runtime_boundary

## Purpose
This file defines how work moves through the system at runtime.

## Input -> decision -> output
- Input: user command, job, or review signal
- Decision: validate, check authority, check conflict, apply guardrails
- Output: event, derived state, and if allowed, a side-effect request

## Runtime rules
- No write action runs without a valid session and lease.
- No action skips the mission kernel.
 - Conflicting writes must be blocked or queued.
- Reliability work does not interrupt delivery unless safety, repeated failure, or contract breach is hit.

## Interaction with other docs
- Should match the non-negotiable rules in `03_guardrail.md`
- Should be consistent with the core decision in `../adr/adr_001_event_driven_control.md`

## What this file does not cover
- Detailed event fields
- Repository-specific scripts
- Provider OPS implementation
