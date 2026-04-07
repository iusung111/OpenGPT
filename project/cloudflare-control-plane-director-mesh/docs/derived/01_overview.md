# 01_overview

## Goal
This system coordinates software delivery with a Cloudflare based control plane while keeping GitHub as the only source of truth for real artifacts.

## System shape
- Control Plane: validates, gates, and records events
- Agent Runtime: performs delivery and reliability work
- Execution Plane: runs GitHub, verify, browser, and deploy side effects
- Artifact Plane: stores docs, paths, and indexes

## Non-negotiable boundaries
- GitHub stores real artifacts.
- Cloudflare stores metadata only.
- All state changes are event-driven.
- Live deploy requires explicit user command.
- One resource cannot have multiple writers.

## Read next
- Behavior and runtime boundaries: `02_runtime_boundary.md`
- Policy and guardrails: `03_guardrail.md`
- Reason for the core model: `../adr/adr_001_event_driven_control.md`

## What this file does not cover
- Event schema details
- Lease semantics
- Workflow input shapes
- Deploy promotion steps
