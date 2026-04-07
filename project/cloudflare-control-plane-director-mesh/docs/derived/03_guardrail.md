# 03_guardrail

## Purpose
This file lists the rules that must not be bypassed during implementation or operation.

## Must-respect rules
- No live deploy without explicit user command.
- No real artifact storage in Cloudflare.
- No multi-writer on the same resource.
- No template mutation at implementation time.
- No proposal should change active work immediately.

## Check order
1. Explicit user command
2. Safety and guardrail
3. Release gate and program direction
4. Quality/hygiene rules
5. Worker proposals

## Interaction rule
- If a lower-level doc conflicts with this file, this file wins.
 - If a code change conflicts with this file, the code change must be rejected or superseded by an explicit decision.

## What this file does not cover
- Complete event model
- PAR flow details
- GitHub path conventions
