from __future__ import annotations

import json
import subprocess
from pathlib import Path


ALLOWED_COMMANDS = {
    "python",
    "python3",
    "pytest",
    "ruff",
    "npm",
    "pnpm",
    "yarn",
    "go",
    "cargo",
    "pwd",
    "echo",
}


def ensure_safe_path(path: str) -> None:
    path_obj = Path(path)
    if path_obj.is_absolute() or ".." in path_obj.parts:
        raise ValueError(f"unsafe path: {path}")


def run_commands(commands: list[list[str]]) -> list[dict]:
    results: list[dict] = []
    for command in commands:
        if not command:
            continue
        if command[0] not in ALLOWED_COMMANDS:
            raise ValueError(f"command not allowlisted: {command[0]}")
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        results.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            }
        )
        if completed.returncode != 0:
            break
    return results


def main() -> int:
    instructions = json.loads(Path(".agent-input/instructions.json").read_text(encoding="utf-8"))
    Path(".agent-output").mkdir(parents=True, exist_ok=True)

    manifest = {
        "job_id": instructions.get("job_id"),
        "auto_improve": instructions.get("auto_improve", False),
        "writes": [],
        "command_results": [],
        "notes": [],
    }

    for item in instructions.get("write_files", []):
        path = item["path"]
        ensure_safe_path(path)
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item["content"], encoding="utf-8")
        manifest["writes"].append(path)

    for item in instructions.get("append_files", []):
        path = item["path"]
        ensure_safe_path(path)
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(item["content"])
        manifest["writes"].append(path)

    command_results = run_commands(instructions.get("commands", []))
    manifest["command_results"] = command_results

    failed = next((item for item in command_results if item["returncode"] != 0), None)
    if instructions.get("auto_improve") and failed is not None:
        manifest["notes"].append("auto improvement requested but requires a new worker cycle")

    Path(".agent-output/manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
