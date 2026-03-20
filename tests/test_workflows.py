from pathlib import Path
import unittest


class PrMergeWorkflowTests(unittest.TestCase):
    def test_delete_branch_flag_assignment_is_single_line(self) -> None:
        content = Path(".github/workflows/pr-merge.yml").read_text(encoding="utf-8")
        self.assertIn('DELETE_FLAG="--delete-branch"', content)
        self.assertNotIn('DELETE_FLAG=\n              "--delete-branch"', content)


class CloudflareLiveDeployWorkflowTests(unittest.TestCase):
    def test_correct_cloudflare_secret_name_is_used(self) -> None:
        content = Path(".github/workflows/cloudflare-live-deploy.yml").read_text(encoding="utf-8")
        self.assertIn("secrets.CLOUDFLARE_ACCOUNT_ID", content)
        self.assertNotIn("secrets.CLOUDFLABE_ACCOUNT_ID", content)

    def test_health_check_gating_uses_env_url(self) -> None:
        content = Path(".github/workflows/cloudflare-live-deploy.yml").read_text(encoding="utf-8")
        self.assertIn("if: ${{ env.LIVE_HEALTHCHECK_URL != '' }}", content)
        self.assertIn("curl --fail --show-error \"${HEADERS[@]}\" \"$LIVE_HEALTHCHECK_URL\"", content)


if __name__ == "__main__":
    unittest.main()
