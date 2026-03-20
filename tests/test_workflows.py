from pathlib import Path
import unittest


class PrMergeWorkflowTests(unittest.TestCase):
    def test_delete_branch_flag_assignment_is_single_line(self) -> None:
        content = Path(".github/workflows/pr-merge.yml").read_text(encoding="utf-8")
        self.assertIn('DELETE_FLAG="--delete-branch"', content)
        self.assertNotIn('DELETE_FLAG=\n              "--delete-branch"', content)


if __name__ == "__main__":
    unittest.main()
