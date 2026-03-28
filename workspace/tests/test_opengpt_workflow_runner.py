from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from workspace.scripts.opengpt_workflow_runner import execute_workflow_request


class OpenGptWorkflowRunnerTests(unittest.TestCase):
    def test_executes_commands_and_copies_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_dir = root / "artifact"
            source_dir = root / "dist"
            source_dir.mkdir(parents=True, exist_ok=True)
            (source_dir / "probe.txt").write_text("probe\n", encoding="utf-8")

            summary = execute_workflow_request(
                request={
                    "kind": "desktop_build",
                    "commands": ['python -c "print(\'runner-ok\')"'],
                    "artifact_paths": ["dist"],
                },
                root_dir=root,
                artifact_dir=artifact_dir,
                default_kind="generic",
            )

            self.assertTrue(summary["ok"])
            self.assertEqual(summary["result"]["overall_status"], "passed")
            self.assertTrue((artifact_dir / "summary.json").exists())
            self.assertTrue((artifact_dir / "logs").exists())
            self.assertTrue((artifact_dir / "outputs" / "dist" / "probe.txt").exists())

    def test_marks_request_without_commands_as_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_dir = root / "artifact"

            summary = execute_workflow_request(
                request={"kind": "verify"},
                root_dir=root,
                artifact_dir=artifact_dir,
                default_kind="generic",
            )

            self.assertTrue(summary["ok"])
            self.assertEqual(summary["result"]["overall_status"], "partial")
            self.assertEqual(summary["steps"][0]["status"], "partial")


if __name__ == "__main__":
    unittest.main()
