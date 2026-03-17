# OpenGPT

Minimal target repository for testing the web ChatGPT + GitHub MCP + GitHub Actions workflow.

## Included

- `.github/workflows/agent-run.yml`
- `.github/workflows/pr-validate.yml`
- `scripts/agent_run.py`
- `tests/test_agent_run.py`

## Purpose

This repository is intentionally small. It exists to validate:

- `workflow_dispatch` from the deployed MCP server
- branch creation on `agent/*`
- dry-run execution
- later PR-based validation
- broader structured command execution for repo inspection, development, and build validation
- Windows GUI / single-file executable verification through `runner_label=windows-latest`

## Structured Agent Payload Notes

`scripts/agent_run.py` now accepts a broader set of development and build commands so web GPT flows can handle:

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
      "content": "import tkinter as tk\nroot = tk.Tk()\nroot.title('OpenGPT Probe')\nlabel = tk.Label(root, text='hello')\nlabel.pack()\nroot.update()\nroot.destroy()\n"
    }
  ],
  "commands": [
    ["python", "-m", "pip", "install", "pyinstaller"],
    ["python", "-m", "PyInstaller", "--onefile", "--windowed", "sample_gui.py"]
  ]
}
```

If the build succeeds, the workflow uploads both `.agent-output/manifest.json` and any `dist/` or `build/` outputs as artifacts.