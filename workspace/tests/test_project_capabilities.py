from __future__ import annotations

import json
import unittest
from pathlib import Path


class ProjectCapabilitiesTests(unittest.TestCase):
    def test_fullstack_contract_points_to_standard_workflows(self) -> None:
        payload = json.loads(
            Path(".opengpt/project-capabilities.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["workflow_ids"]["verify"], "opengpt-exec.yml")
        self.assertEqual(payload["workflow_ids"]["package"], "opengpt-package.yml")
        self.assertFalse(payload["web_preview"]["enabled"])

    def test_capabilities_include_verify_and_desktop_profiles(self) -> None:
        payload = json.loads(
            Path(".opengpt/project-capabilities.json").read_text(encoding="utf-8")
        )
        profile_ids = {entry["id"] for entry in payload["verify_profiles"]}
        self.assertIn("python-unit", profile_ids)
        self.assertIn("desktop-build-probe", profile_ids)
        self.assertIn("desktop-smoke-probe", profile_ids)


if __name__ == "__main__":
    unittest.main()
