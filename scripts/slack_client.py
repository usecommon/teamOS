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
