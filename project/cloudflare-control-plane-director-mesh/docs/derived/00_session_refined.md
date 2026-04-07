# 00_session_refined (re-built from raw session log)

## Purpose
This document is a derived working source built by extracting structured intent from the raw session transcript.
It removes conversation noise and keeps only actionable design content.

This file is a source-of-intent and must be used before any other derived docs.

## Raw source
- docs/source/session_transcript_visible_chat_detailed.md

## Extracted core goals
- Build an autonous software delivery system under a Cloudflare control plane
- Separate control metadata and real artifact storage strictly
- Enforce deterministic execution and authority ordering
- Eliminate implicit approval and manual gates with exception of live deploy

## Extracted non-negotiable rules
- All state changes must be represented as events
- Event log is append-only (no overwrite)
- GitHub is a single source of truth for artifacts
- Cloudflare stores metadata only
- No multi-writer on the same resource
- Live deploy requires explicit user command
- All actions must pass through a central decision layer (Mission Kernel)

## Extracted architecture shape
- Control Plane
  - program director
  - release gate
  - quality hygiene board
  - session broker
  - mission kernel
- Agent Runtime
  - delivery pod
  - reliability pod
- Execution Plane
  - github
  - verify
  - deploy
- Artifact Plane
  - docs
  - registry
  - path index

## Extracted execution model
- event-driven processing
- validate -> authority -> dedup -> conflict -> guardrail -> event emit -> state derive
- no direct state mutation

## Extracted session model
- all agents operate via sessions
- each session has a lease
- lease expiration revokes write authority
- no shared write access

$# Extracted delivery vs reliability lane
- delivery implements features
- reliability analyzes and improves
- reliability cannot interrupt delivery unless threshold violated

## Extracted deployment policy
- mirror deploy is automated
- live deploy requires user command
- no implicit deploy trigger

## Extracted artifact rule
- all outputs must be stored in GitHub
- cloudflare stores metadata only
- artifacts must be path-indexed

## Open items
- event schema details not yet defined
- session lease format not defined
- conflict resolution strategy partially undefined
- runtime file interfaces not defined

## Usage
- Use this file as the single intent reference
- All derived docs must be consistent with this file
- Do not add implementation details here

## What this file does not cover
- raw conversation
- code logic
- API specs
