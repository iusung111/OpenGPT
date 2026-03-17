from __future__ import annotations

import unittest

from scripts.agent_run import (
    ensure_safe_path,
    is_command_allowed,
    is_protected_branch_command,
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
