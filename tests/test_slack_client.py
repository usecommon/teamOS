"""FK5/FK6 delivery clients: dry-run by default, real Slack only with a token.
No network is touched here — HttpSlackClient is constructed but never called."""
import os
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import slack_client  # noqa: E402


class DeliveryClients(unittest.TestCase):
    def test_factory_dry_run_without_token(self):
        os.environ.pop("SLACK_BOT_TOKEN", None)
        c = slack_client.from_env_or_dry()
        self.assertIsInstance(c, slack_client.DryRunSlack)

    def test_factory_real_client_with_token(self):
        os.environ["SLACK_BOT_TOKEN"] = "xoxb-test"
        try:
            c = slack_client.from_env_or_dry()
            self.assertIsInstance(c, slack_client.HttpSlackClient)
        finally:
            os.environ.pop("SLACK_BOT_TOKEN", None)

    def test_dry_run_posts_without_network(self):
        c = slack_client.DryRunSlack()
        ts = c.post_message("DM_X", "hello")
        self.assertEqual(ts, "dry-run-0")
        self.assertEqual(c.sent, [("DM_X", "hello")])
        self.assertEqual(c.reactions_get("DM_X", ts), [])

    def test_reactions_get_raises_on_api_error(self):
        # a swallowed error would deflate the A-A4 floor — must raise, not [].
        c = slack_client.HttpSlackClient("xoxb-test")
        c._call = lambda method, payload: {"ok": False, "error": "invalid_auth"}
        with self.assertRaises(RuntimeError):
            c.reactions_get("C1", "1.0")
        c._call = lambda method, payload: {"ok": True, "message": {
            "reactions": [{"name": "white_check_mark", "users": ["U1"]}]}}
        self.assertEqual(c.reactions_get("C1", "1.0"),
                         [{"name": "white_check_mark", "users": ["U1"]}])


if __name__ == "__main__":
    unittest.main()
