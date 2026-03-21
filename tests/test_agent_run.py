from __future__ import annotations

import unittest

from scripts.agent_run import (
    build_pull_request_merge_command,
    build_review_context,
    ensure_project_scaffold,
    ensure_safe_path,
    is_command_allowed,
    is_protected_branch_command,
    normalize_project_slug,
    normalize_review_findings,
    normalize_review_verdict,
    validate_command,
)


class AgentRunSafetyTests(unittest.TestCase):
    def test_blocks_parent_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsafe path"):
            ensure_safe_path("../outside.txt")

    def test_blocks_absolute_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsafe path"):
            ensure_safe_path("/tmp/outside.txt")

    def test_allows_repo_relative_path(self) -> None:
        ensure_safe_path("dist/app.exe")


class AgentRunProjectMetadataTests(unittest.TestCase):
    def test_normalizes_valid_project_slug(self) -> None:
        self.assertEqual(normalize_project_slug("chat-ui"), "chat-ui")

    def test_rejects_invalid_project_slug(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid project_slug"):
            normalize_project_slug("Chat UI")

    def test_feature_delivery_requires_project_slug(self) -> None:
        manifest = {"writes": [], "notes": [], "review_context": {"cycle": 0}}
        with self.assertRaisesRegex(ValueError, "project_slug is required"):
            ensure_project_scaffold(
                project_slug=None,
                request_kind="feature_delivery",
                create_project_scaffold=False,
                manifest=manifest,
            )


class AgentRunReviewLoopTests(unittest.TestCase):
    def test_normalizes_review_verdict(self) -> None:
        self.assertEqual(normalize_review_verdict(" Changes_Requested "), "changes_requested")

    def test_rejects_invalid_review_verdict(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid review_verdict"):
            normalize_review_verdict("retry")

    def test_normalizes_review_findings(self) -> None:
        findings = normalize_review_findings(
            [
                {
                    "severity": "HIGH",
                    "file": "scripts/agent_run.py",
                    "line_hint": "120",
                    "rationale": "Persist review context in manifest.",
                }
            ]
        )
        self.assertEqual(findings[0]["severity"], "high")
        self.assertEqual(findings[0]["line_hint"], "120")

    def test_rejects_invalid_review_findings(self) -> None:
        with self.assertRaisesRegex(ValueError, "review finding rationale is required"):
            normalize_review_findings(
                [
                    {
                        "severity": "low",
                        "file": "README.md",
                    }
                ]
            )

    def test_builds_review_context(self) -> None:
        context = build_review_context(
            {
                "review_cycle": 2,
                "review_verdict": "approved",
                "next_action": "merge after validation",
                "review_findings": [],
            }
        )
        self.assertEqual(context["cycle"], 2)
        self.assertEqual(context["verdict"], "approved")
        self.assertEqual(context["next_action"], "merge after validation")


class AgentRunAllowlistTests(unittest.TestCase):
    def test_allows_common_repo_inspection_commands(self) -> None:
        self.assertTrue(is_command_allowed(["ls"]))
        self.assertTrue(is_command_allowed(["sed", "-n", "1,20p", "README.md"]))
        self.assertTrue(is_command_allowed(["git", "status", "--short"]))

    def test_allows_windows_gui_build_tooling(self) -> None:
        self.assertTrue(is_command_allowed(["pip", "install", "pyinstaller"]))
        self.assertTrue(
            is_command_allowed(
                ["python", "-m", "PyInstaller", "--onefile", "--windowed", "sample_gui.py"]
            )
        )
        self.assertTrue(is_command_allowed(["powershell", "-Command", "Get-ChildItem"]))

    def test_blocks_unlisted_commands(self) -> None:
        self.assertFalse(is_command_allowed([]))
        self.assertFalse(is_command_allowed(["curl", "-I", "https://example.com"]))


class AgentRunStructuredOperationTests(unittest.TestCase):
    def test_builds_pull_request_merge_command(self) -> None:
        self.assertEqual(
            build_pull_request_merge_command(
                {
                    "number": 7,
                    "method": "merge",
                    "repository": "iusung111/OpenGPT",
                }
            ),
            ["gh", "pr", "merge", "7", "--merge", "--repo", "iusung111/OpenGPT"],
        )

    def test_builds_pull_request_merge_command_with_delete_branch(self) -> None:
        self.assertEqual(
            build_pull_request_merge_command(
                {
                    "number": "8",
                    "method": "squash",
                    "delete_branch": True,
                }
            ),
            ["gh", "pr", "merge", "8", "--squash", "--delete-branch"],
        )

    def test_rejects_invalid_merge_method(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported merge method"):
            build_pull_request_merge_command({"number": 7, "method": "fast-forward"})

    def test_rejects_unsafe_repository(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsafe repository"):
            build_pull_request_merge_command({"number": 7, "repository": "iusung111/OpenGPT  bad"})


class AgentRunProtectedBranchTests(unittest.TestCase):
    def test_detects_direct_push_to_main(self) -> None:
        self.assertTrue(is_protected_branch_command(["kit", "push", "origin", "main"]))
