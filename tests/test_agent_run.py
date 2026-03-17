from __future__ import annotations

import unittest

from scripts.agent_run import build_pull_request_merge_command, ensure_safe_path, is_command_allowed


class AgentRunSafetyTests(unittest.TestCase):
    def test_blocks_parent_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsafe path"):
            ensure_safe_path("../outside.txt")

    def test_blocks_absolute_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsafe path"):
            ensure_safe_path("/tmp/outside.txt")

    def test_allows_repo_relative_path(self) -> None:
        ensure_safe_path("dist/app.exe")


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
            build_pull_request_merge_command({"number": 7, "repository": "iusung111/OpenGPT bad"})


if __name__ == "__main__":
    unittest.main()
