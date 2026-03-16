from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


CORE_COMMANDS = {
    "pwd",
    "echo",
    "env",
    "printenv",
    "ls",
    "cat",
    "sed",
    "grep",
    "find",
    "head",
    "tail",
    "wc",
    "cp",
    "mv",
    "mkdir",
    "rm",
    "touch",
}

PYTHON_COMMANDS = {
    "python",
    "python3",
    "pip",
    "pip3",
    "pytest",
    "ruff",
    "pyinstaller",
    "nuitka",
    "uv",
    "uvx",
}

NODE_COMMANDS = {
    "node",
    "npm",
    "pnpm",
    "yarn",
    "npx",
}

NATIVE_BUILD_COMMANDS = {
    "go",
    "cargo",
    "rustc",
    "cmake",
    "cpack",
    "make",
}

VCS_COMMANDS = {
    "git",
    "gh",
}

WINDOWS_COMMANDS = {
    "pwsh",
    "powershell",
}

ALLOWED_COMMANDS = (
    CORE_COMMANDS
    | PYTHON_COMMANDS
    | NODE_COMMANDS
    | NATIVE_BUILD_COMMANDS
    | VCS_COMMANDS
    | WINDOWS_COMMANDS
)

REPOSITORY_SLEG_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MERGE_METHOD_FLAGS = {
    "merge": "--merge",
    "squash": "--squash",
    "rebase": "--rebase",
}


def is_command_allowed(command: list[str]) -> bool:
    return bool(command) and command[0] in ALLOWED_COMMANDS


def ensure_safe_path(path: str) -> None:
    path_obj = Path(path)
    if path_obj.is_absolute() or ".." in path_obj.parts:
        raise ValueError(f"unsafe path: {path}")


def ensure_safe_repository(repository: str) -> None:
    if not REPOSITORY_SLEG_RE.fullmatch(repository):
        raise ValueError(f"unsafe repository: {repository}")


def normalize_pull_request_number(value: int | str) -> str:
    if isinstance(value, int):
        number = value
    elif isinstance(value, str) and value.isdigit():
        number = int(value)
    else:
        raise ValueError("pull request number must be a positive integer")

    if number <= 0:
        raise ValueError("pull request number must be a positive integer")
    return str(number)


def build_pull_request_merge_command(pull_request_merge: dict) -> list[str]:
    if "number" not in pull_request_merge:
        raise ValueError("pull request merge requires a number")

    method = pull_request_merge.get("method", "merge")
    if method not in MERGE_METHOD_FLAGS:
        raise ValueError(f"unsupported merge method: {method}")

    command = [
        "gh",
        "pr",
        "merge",
        normalize_pull_request_number(pull_request_merge["number"]),
        MERGE_METHOD_FLAGS[method],
    ]

    repository = pull_request_merge.get("repository")
    if repository:
        ensure_safe_repository(repository)
        command.extend(["--repo", repository])

    if pull_request_merge.get("delete_branch", False):
        command.append("--delete-branch")

    return command


def run_commands(commands: list[list[str]]) -> list[dict]:
    results: list[dict] = []
    for command in commands:
        if not command:
            continue
        if not is_command_allowed(command):
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
        "structured_operations": [],
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

    command_results: list[dict] = []

    pull_request_merge = instructions.get("pull_request_merge")
    if pull_request_merge:
        pull_request_merge_result = run_commands([build_pull_request_merge_command(pull_request_merge)])[0]
        manifest["structured_operations"].append(
            {
                "type": "pull_request_merge",
                "result": pull_request_merge_result,
            }
        )
        manifest["notes"].append("used structured pull request merge operation inside agent-run")
        command_results.append(pull_request_merge_result)

    failed = next((item for item in command_results if item["returncode"] != 0), None)
    if failed is None:
        command_results.extend(run_commands(instructions.get("commands", [])))

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
