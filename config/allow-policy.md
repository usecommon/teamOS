# Team OS — Allow Policy (WO-4)
#
# Irreversible actions — external send, mutation, disclosure, destruction, spend
# — DENY BY DEFAULT: each one asks for your confirmation unless it matches a rule
# below. This file is YOURS. Edit freely; the agent cannot (config/ is a
# protected path — the agent can't loosen its own boundary).
#
# It ships with exactly ONE rule: the agent may DELIVER TO YOU (its principal)
# without asking every time — so your Day One Brief and digests arrive done.
# Everything else irreversible (deploy, delete, payment, external email, posting
# OUTSIDE your delivery channel) stays deny-by-default until YOU add a rule.
#
# One rule per line (a line starting with '#' is a comment):
#     <tool-substring>  [target-substring ...]
#   tool-substring   — matched (case-insensitive) inside the tool name
#   target-substring — optional; ALL listed must appear inside the action's target
#
# TIGHTEN the shipped delivery rule to your own DM by adding your channel id:
#     slack_post_message  D0123456789
#
# More examples (commented — delete the leading '#  ' to pre-authorize):
#   mail    @mycompany.com     allow email only to internal addresses
#   deploy  staging            allow deploys only to staging
#
# The guarantee: no irreversible action is auto-permitted without a match here,
# and every one is recorded before it acts.

slack_post_message
