# OpenGPT

Minimal target repository for testing the web ChatGPT + GitHub MCP + GitHub Actions workflow.

## Root Layout

- `.github/`
- `project/`
- `workspace/`
- `README.md`
- `wrangler.toml`

`.github/`, `.gitignore`, and `wrangler.toml` stay at the repository root because GitHub Actions, git ignore rules, and Cloudflare Worker deploy tooling expect them there.

## Included

- `.github/workflows/agent-run.yml`
- `.github/workflows/pr-validate.yml`
- `.github/workflows/cloudflare-live-deploy.yml`
- `workspace/`
- `workspace/scripts/agent_run.py`
- `workspace/tests/test_agent_run.py`
- `wrangler.toml`
- `workspace/src/worker.js`
- `project/`

## Purpose

This repository is intentionally small. It exists to validate:

- `workflow_dispatch` from the deployed MCP server
- branch creation on `agent/*`
- dry-run execution
- later PR-based validation
- broader structured command execution for repo inspection, development, and build validation
- Windows GUI / single-file executable verification through `runner_label=windows-latest`
- future chat-requested feature delivery with per-project tracking under `project/`
- live Cloudflare deploy triggered from GitHub Actions on `main`

## Cloudflare Live Deploy

The `.github/workflows/cloudflare-live-deploy.yml` workflow deploys the repository's Worker on push to `main` (and can also be run manually). It now expects a minimal Worker project in this repository:

- `wrangler.toml`
- `workspace/src/worker.js`

The workflow:

- validates `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`
- validates that the Worker config and entrypoint exist before deploying
- installs Wrangler and runs `wrangler deploy --config wrangler.toml`
- optionally performs a health check via `LIVE_HEALTHCHECK_URL`

Required secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Optional secrets:

- `LIVE_HEALTHCHECK_URL`
- `LIVE_HEALTHCHECK_TOKEN`

## Chat-Requested Feature Delivery Flow

When the MCP workflow matures past self-improvement, chat-requested implementation work should use the structured project metadata below:

- `request_kind=feature_delivery` for user-requested implementation work
- `project_slug=<short-kebab-name>` to create a stable project identity
- `create_project_scaffold=true` to create:
  - `project/<project_slug>/README.md`
- non-dry-run execution so the workflow creates an `agent/<job_id>-<project_slug>-<run_id>` branch and opens a PR

This keeps feature work isolated from the MCP self-improvement loop while preserving a dedicated project folder for notes and deliverables.

## Structured Agent Payload Notes

`workspace/scripts/agent_run.py` now accepts a broader set of development and build commands so web GPT flows can handle:

- repo inspection: `ls`, `cat`, `sed`, `grep`, `find`
- Python workflows: `python`, `python3`, `pip`, `pip3`, `pytest`, `ruff`, `pyinstaller`, `uv`
- Node workflows: `node`, `npm`, `pnpm`, `yarn`, `npx`
- native build workflows: `go`, `cargo`, `rustc`, `cmake`, `cpack`, `make`
- GitHub and VCS helpers: `git`, `gh`
- Windows runner helpers: `pwsh`, `powershell`
- PR merge through structured payload: `pull_request_merge`

The workflow also accepts a `runner_label` input so the same structured payload can be validated on `ubuntu-latest` or `windows-latest`.

## Example: Structured PR Merge

Use the existing allowlisted `agent-run.yml` workflow and pass a structured `pull_request_merge` object instead of adding a separate merge workflow:

```json
{
  "pull_request_merge": {
    "number": 7,
    "method": "merge",
    "repository": "iusung111/OpenGPT"
  }
}
```

This keeps PR merge inside the existing allowlisted workflow surface and reduces extra allowlist churn for one-off workflow files.

## Example: Windows GUI One-File Build

Use `runner_label=windows-latest` and a structured payload that writes a tiny GUI script, installs PyInstaller, and builds it:

 ```json
{
  "write_files": [
    {
      "path": "sample_gui.py",
      "content": "import tkinter as tk\\nroot = tk.Tk()\\nroot.title('OpenGPT Probe')\\nlabel = tk.Label(root, text='hello')\\nlabel.pack()\\nroot.update()\\nroot.destroy()\\n"
    }
  ],
  "commands": [
    ["python", "-m", "pip", "install", "pyinstaller"],
    ["python", "-m", "PyInstaller", "--onefile", "--windowed", "sample_gui.py"]
  ]
}
```

If the build succeeds, the workflow uploads both `.agent-output/manifest.json` and any `dist/` or `build/` outputs as artifacts.
