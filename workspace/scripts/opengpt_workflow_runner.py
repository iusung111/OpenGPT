from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any


def decode_request() -> dict[str, Any]:
    explicit = os.environ.get("OPENGPT_REQUEST_B64", "").strip()
    if explicit:
        return json.loads(base64.b64decode(explicit).decode("utf-8"))

    event_path = os.environ.get("GITHUB_EVENT_PATH", "").strip()
    if not event_path:
        return {}

    payload_path = Path(event_path)
    if not payload_path.exists():
        return {}

    event_payload = json.loads(payload_path.read_text(encoding="utf-8"))
    request_b64 = str(event_payload.get("inputs", {}).get("request_b64", "") or "").strip()
    if not request_b64:
        return {}
    return json.loads(base64.b64decode(request_b64).decode("utf-8"))


def sanitize_name(value: Any, fallback: str) -> str:
    sanitized = "".join(
        character.lower() if str(character).isalnum() else "-"
        for character in str(value or fallback)
    ).strip("-")
    while "--" in sanitized:
        sanitized = sanitized.replace("--", "-")
    return (sanitized[:48] or fallback).strip("-") or fallback


def ensure_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"artifact path must be repo-relative: {value}")
    return path


def copy_artifact_paths(root_dir: Path, artifact_dir: Path, relative_paths: list[str]) -> list[str]:
    copied: list[str] = []
    outputs_dir = artifact_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    for relative_path in relative_paths:
        if not isinstance(relative_path, str) or not relative_path.strip():
            continue
        safe_relative = ensure_relative_path(relative_path.strip())
        source_path = root_dir / safe_relative
        if not source_path.exists():
            continue
        destination_path = outputs_dir / safe_relative
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.is_dir():
            shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, destination_path)
        copied.append(safe_relative.as_posix())
    return copied


def run_command(command: str, env: dict[str, str]) -> dict[str, Any]:
    started_at = time.time()
    completed = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    return {
        "command": command,
        "exit_code": int(completed.returncode),
        "stdout": completed.stdout or "",
        "stderr": completed.stderr or "",
        "duration_ms": int((time.time() - started_at) * 1000),
    }


def execute_workflow_request(
    *,
    request: dict[str, Any],
    root_dir: Path,
    artifact_dir: Path,
    default_kind: str,
    default_artifact_paths: list[str] | None = None,
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = artifact_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    raw_commands = request.get("commands", [])
    commands = [
        str(item).strip()
        for item in raw_commands
        if isinstance(item, str) and item.strip()
    ]
    query_command = request.get("query_command")
    if isinstance(query_command, str) and query_command.strip():
        commands.append(query_command.strip())

    steps: list[dict[str, Any]] = []
    overall_status = "passed"

    base_env = os.environ.copy()
    base_env["OPENGPT_REQUEST_KIND"] = str(request.get("kind") or default_kind)
    base_env["OPENGPT_QUERY_TEXT"] = (
        str(request.get("query_text"))
        if isinstance(request.get("query_text"), str)
        else ""
    )

    for index, command in enumerate(commands, start=1):
        result = run_command(command, base_env)
        name = f"{index:02d}-{sanitize_name(command, f'step-{index}')}"
        (logs_dir / f"{name}.stdout.log").write_text(result["stdout"], encoding="utf-8")
        (logs_dir / f"{name}.stderr.log").write_text(result["stderr"], encoding="utf-8")
        step_names = request.get("step_names")
        step_name = (
            step_names[index - 1]
            if isinstance(step_names, list)
            and len(step_names) >= index
            and isinstance(step_names[index - 1], str)
            else command
        )
        status = "passed" if result["exit_code"] == 0 else "failed"
        steps.append(
            {
                "name": step_name,
                "status": status,
                "exit_code": result["exit_code"],
                "duration_ms": result["duration_ms"],
                "stdout_excerpt": result["stdout"][-4000:],
                "stderr_excerpt": result["stderr"][-4000:],
            }
        )
        if status == "failed":
            overall_status = "failed"
            if request.get("continue_on_error") is not True:
                break

    if not commands:
        overall_status = "partial"
        steps.append(
            {
                "name": str(request.get("kind") or default_kind),
                "status": "partial",
                "exit_code": 0,
                "duration_ms": 0,
                "stdout_excerpt": "",
                "stderr_excerpt": "no commands were configured for this request",
            }
        )

    configured_artifact_paths = (
        request.get("artifact_paths")
        if isinstance(request.get("artifact_paths"), list)
        else (default_artifact_paths or [])
    )
    copied_artifacts = copy_artifact_paths(
        root_dir,
        artifact_dir,
        [path for path in configured_artifact_paths if isinstance(path, str)],
    )

    summary = {
        "ok": overall_status != "failed",
        "kind": str(request.get("kind") or default_kind),
        "request": {
            "profile_id": request.get("profile_id"),
            "label": request.get("label"),
            "deploy_target": request.get("deploy_target"),
            "package_targets": request.get("package_targets", [])
            if isinstance(request.get("package_targets"), list)
            else [],
        },
        "result": {
            "overall_status": overall_status,
            "step_count": len(steps),
            "passed_steps": sum(1 for step in steps if step["status"] == "passed"),
            "failed_steps": sum(1 for step in steps if step["status"] == "failed"),
        },
        "steps": steps,
        "outputs": {
            "preview": request.get("preview"),
            "release": request.get("release"),
            "copied_artifacts": copied_artifacts,
        },
    }

    (artifact_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    (artifact_dir / "request.json").write_text(
        json.dumps(request, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--default-kind", default="generic")
    parser.add_argument("--artifact-path", action="append", default=[])
    args = parser.parse_args()

    summary = execute_workflow_request(
        request=decode_request(),
        root_dir=Path.cwd(),
        artifact_dir=Path.cwd() / args.artifact_dir,
        default_kind=args.default_kind,
        default_artifact_paths=args.artifact_path,
    )
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
