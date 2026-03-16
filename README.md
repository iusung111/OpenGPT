# OpenGPT

Minimal target repository for testing the web ChatGPT + GitHub MCP + GitHub Actions workflow.

## Included

- `.github/workflows/agent-run.yml`
- `.github/workflows/pr-validate.yml`
- `scripts/agent_run.py`

## Purpose

This repository is intentionally small. It exists to validate:

- `workflow_dispatch` from the deployed MCP server
- branch creation on `agent/*`
- dry-run execution
- later PR-based validation
