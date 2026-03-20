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

PROTECTED_BRANCHES = {"main", "master"}
PROJECT_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPOSITORY_SLUG_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MERGE_METHOD_FLAGS = {
    "merge": "--merge",
    "squash": "--squash",
    "rebase": "--rebase",
}

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
    raw_path = str(path)
    if (
        path_obj.is_absolute()
        or raw_path.startswith(("/", "\\"))
        or re.match(r"^[A-Za-z]:[\\/]", raw_path) is not None
        or ".." in path_obj.parts
    ):
        raise ValueError(f"unsafe path: {path}")


def normalize_project_slug(project_slug: str | None) -> str | None:
    if project_slug is None:
        return None
    slug = project_slug.strip()
    if not slug:
        return None
    if not PROJECT_SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"invalid project_slug: {project_slug}")
    return slug


def ensure_safe_repository(repository: str) -> None:
    if not REPOSITORY_SLUG_PATTERN.fullmatch(repository):
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


def project_doc_path(project_slug: str) -> Path:
    return Path("docs/projects") / f"{project_slug}.md"


def project_root_path(project_slug: str) -> Path:
    return Path("projects") / project_slug


def ensure_project_scaffold(
    *,
    project_slug: str | None,
    request_kind: str,
    create_project_scaffold: bool,
    manifest: dict,
) -> None:
    if request_kind != "feature_delivery":
        return
    if project_slug is None:
        raise ValueError("project_slug is required when request_kind=feature_delivery")
    manifest["notes"].append(f"feature delivery project slug: {project_slug}")
    if not create_project_scaffold:
        return

    doc_path = project_doc_path(project_slug)
    ensure_safe_path(str(doc_path))
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    if not doc_path.exists():
        doc_path.write_text(
            "\n".join(
                [
                    f"# Project: {project_slug}",
                    "",
                    "- Request kind: feature_delivery",
                    "- Status: scaffolded",
                    "- Notes: created automatically by agent_run.py",
                    "",
                    "## Scope",
                    "",
                    "Fill in the chat-requested implementation scope here.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        manifest["writes"].append(str(doc_path))

    root_path = project_root_path(project_slug)
    ensure_safe_path(str(root_path))
    root_path.mkdir(parents=True, exist_ok=True)
    keep_path = root_path / ".gitkeep"
    if not keep_path.exists():
        keep_path.write_text("", encoding="utf-8")
        manifest["writes"].append(str(keep_path))


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

    request_kind = instructions.get("request_kind", "self_improvement")
    project_slug = normalize_project_slug(instructions.get("project_slug"))
    create_project_scaffold = bool(instructions.get("create_project_scaffold", False))

    manifest = {
        "job_id": instructions.get("job_id"),
        "auto_improve": instructions.get("auto_improve", False),
        "request_kind": request_kind,
        "project_slug": project_slug,
        "project_doc": str(project_doc_path(project_slug)) if project_slug else None,
        "project_root": str(project_root_path(project_slug)) if project_slug else None,
        "writes": [],
        "command_results": [],
        "structured_operations": [],
        "notes": [],
    }

    ensure_project_scaffold(
        project_slug=project_slug,
        request_kind=request_kind,
        create_project_scaffold=create_project_scaffold,
        manifest=manifest,
    )

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
