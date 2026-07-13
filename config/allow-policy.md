# Team OS — Allow Policy (WO-4)
#
# Irreversible actions — external send, mutation, disclosure, destruction, spend
# — DENY BY DEFAULT: each one asks for your confirmation unless it matches a rule
# below. This file is YOURS. It ships EMPTY (only these comments), so nothing
# irreversible happens unattended until you say so. Loosening the exterior
# boundary is your owned, attributed choice — the tool ships no opinion of harm,
# only "irreversible acts need explicit say-so."
#
# One rule per line (a line starting with '#' is a comment):
#     <tool-substring>  [target-substring ...]
#   tool-substring   — matched (case-insensitive) inside the tool name
#   target-substring — optional; ALL listed must appear inside the action's target
#
# Examples (commented out — delete the leading '#  ' to pre-authorize):
#   post    #team-standup      allow posting only to #team-standup
#   mail    @mycompany.com     allow email only to internal addresses
#   deploy  staging            allow deploys only to staging
#
# The guarantee: no irreversible action is auto-permitted without a match here,
# and every one is recorded before it acts. config/ is a protected path — the
# agent cannot edit this file; only you can.
