"""Slack client interface + an in-memory fake for tests.

The real client wraps chat.postMessage + reactions.get. The fake keeps message
TEXT and REACTIONS strictly separate — reactions come only from the reactions
API, never parsed from message text (SE-1: a forged textual 'reaction report'
must not become an L8 signal).
"""


class SlackClient:
    def post_message(self, channel, text, blocks=None):
        raise NotImplementedError

    def reactions_get(self, channel, ts):
        raise NotImplementedError


class FakeSlack(SlackClient):
    def __init__(self):
        self._ts = 0
        self.messages = {}       # (channel, ts) -> {text, blocks}
        self._reactions = {}     # (channel, ts) -> {name: set(user_id)}

    def post_message(self, channel, text, blocks=None):
        self._ts += 1
        ts = f"{self._ts:.6f}"
        self.messages[(channel, ts)] = {"text": text, "blocks": blocks or []}
        self._reactions[(channel, ts)] = {}
        return ts

    # test helper: simulate a real emoji tap by a specific user
    def add_reaction(self, channel, ts, name, user_id):
        self._reactions.setdefault((channel, ts), {}).setdefault(name, set()).add(user_id)

    def reactions_get(self, channel, ts):
        agg = self._reactions.get((channel, ts), {})
        return [{"name": name, "users": sorted(users)} for name, users in agg.items()]


class DryRunSlack(SlackClient):
    """Prints instead of sending — the default until a real target + token are
    configured. Lets the live pipeline run end-to-end (through the gate) with no
    network side effect, so the streak scaffolding is exercisable safely."""
    def __init__(self):
        self.sent = []

    def post_message(self, channel, text, blocks=None):
        self.sent.append((channel, text))
        print(f"[dry-run] would post to {channel}:\n{text}\n")
        return "dry-run-0"

    def reactions_get(self, channel, ts):
        return []


class HttpSlackClient(SlackClient):
    """Real Slack Web API client (stdlib urllib — no new deps). Only constructed
    when a bot token is present; and the SEND still traverses the FK2 gate in
    day_one_brief.deliver() BEFORE this posts. reactions come from reactions.get
    only, never message text (SE-1)."""
    def __init__(self, token):
        self.token = token

    def _call(self, method, payload):
        import json as _json
        import urllib.request
        req = urllib.request.Request(
            f"https://slack.com/api/{method}",
            data=_json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json; charset=utf-8"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return _json.loads(r.read())

    def post_message(self, channel, text, blocks=None):
        resp = self._call("chat.postMessage", {"channel": channel, "text": text, "blocks": blocks or []})
        if not resp.get("ok"):
            raise RuntimeError(f"slack chat.postMessage error: {resp.get('error')}")
        return resp["ts"]

    def reactions_get(self, channel, ts):
        resp = self._call("reactions.get", {"channel": channel, "timestamp": ts})
        msg = resp.get("message", {})
        return [{"name": r["name"], "users": r["users"]} for r in msg.get("reactions", [])]


def from_env_or_dry(token_env="SLACK_BOT_TOKEN"):
    """Real client when a bot token is set; otherwise a safe dry-run client."""
    import os
    tok = os.environ.get(token_env)
    return HttpSlackClient(tok) if tok else DryRunSlack()
