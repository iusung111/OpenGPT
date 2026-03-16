# OpenGPT

Minimal target repository for testing the web ChatGPT + GitHub MCP + GitHub Actions workflow.

## Included

- `.github/workflows/agent-run.yml`: entry workflow for MCP-triggered agent runs
- `.github/workflows/pr-validate.yml`: PV
 validation workflow for changes opened through pull requests
- `scripts/agent_run.py`: helper script used by the agent run workflow

## Purpose

This repository is intentionally small. It exists to validate:

- `workflow_dispatch` from the deployed MCP server
- branch creation on `agent/*`
- dry-run execution
- later PR-based validation
