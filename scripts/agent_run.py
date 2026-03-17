from __future__ import annotations

import json
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

PROTECTED_BRANCHES = {"main", "master"}

ALLOWED_COMMANDS = (
    CORE_COMMANDS
    | PYTHON_COMMANDS
    | NODE_COMMANDS
    | NATIVE_BUILD_COMMANDS
    | VCS_COMMANDS
    | WINDOWS_COMMANDS
)


def is_command_allowed(command: list[str]) -> bool:
    return bool(command) and command[0] in ALLOWED_COMMANDS


def ensure_safe_path(path: str) -> None:
    path_obj = Path(path)
    if path_obj.is_absolute() or ".." in path_obj.parts:
        raise ValueError(f"unsafe path: {path}")


def _extract_git_push_targets(command: list[str]) -> list[str]:
    if len(command) < 4 or command[0] != "git" or command[1] != "push":
        return []
    targets: list[str] = []
    options_with_values = {"--repo", "--receive-pack", "--exec", "--upload-pack"}
    i = 2
    while i < len(command):
        token = command[i]
        if token == "--":
            targets.extend(command[i + 1 :])
            break
        if token in options_with_values:
            i += 2
            continue
        if token.startswith("-"):
            i += 1
            continue
        targets.extend(command[i + 1 :])
        break
    return targets


def is_protected_branch_command(command: list[str]) -> bool:
    if not command:
        return False
    if command[0] == "git":
        push_targets = _extract_git_push_targets(command)
        return any(target in PROTECTED_BRANCHES for target in push_targets)
    if command[0] == "gh" and len(command) >= 4:
        if command[1:3] == ["pr", "merge"]:
            for token in command[3:]:
                if token in {"--admin", "--delete-branch"}:
                    continue
                if token.startswith("-"):
                    continue
                return token in PROTECTED_BRANCHES
    return False


def validate_command(command: list[str]) -> None:
    if not is_command_allowed(command):
        raise ValueError(f"command not allowlisted: {command[0]}")
    if is_protected_branch_command(command):
        raise ValueError("direct protected branch mutation is not allowed; use PR merge flow")


def run_commands(commands: list[list[str]]) -> list[dict]:
    results: list[dict] = []
    for command in commands:
        if not command:
            continue
        validate_command(command)
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