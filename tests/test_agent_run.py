from __future__ import annotations

import unittest

from scripts.agent_run import (
    build_pull_request_merge_command,
    ensure_project_scaffold,
    ensure_safe_path,
    is_command_allowed,
    is_protected_branch_command,
    normalize_project_slug,
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
        manifest = {"writes": [], "notes": []}
        with self.assertRaisesRegex(ValueError, "project_slug is required"):
            ensure_project_scaffold(
                project_slug=None,
                request_kind="feature_delivery",
                create_project_scaffold=False,
                manifest=manifest,
            )


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
        self.assertTrue(is_protected_branch_command(["git", "push", "origin", "main"]))

    def test_detects_direct_push_to_master_with_options(self) -> None:
        self.assertTrue(
            is_protected_branch_command(
                ["git", "push", "--set-upstream", "origin", "master"]
            )
        )

    def test_allows_push_to_agent_branch(self) -> None:
        self.assertFalse(
            is_protected_branch_command(
                ["git", "push", "--set-upstream", "origin", "agent/safe-branch"]
            )
        )

    def test_blocks_validation_for_protected_branch_mutation(self) -> None:
        with self.assertRaisesRegex(ValueError, "protected branch mutation"):
            validate_command(["git", "push", "origin", "main"])


if __name__ == "__main__":
    unittest.main()
