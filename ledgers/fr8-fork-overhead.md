# FR8 — fork-overhead ledger (weekly, one line per week)

The speed thesis has a ledger (EC-1). One line per week: hours on fork-overhead
(adapter, shims, harness-drift) vs. hours on kernel (schemas, gates, loops,
compiler — work mainline would also need). **Pre-registered abort threshold:
overhead >40% of total hours for 3 consecutive weeks → reassess the vehicle at
that moment, not at merge-back by sunk cost.**

| week (UTC) | overhead hrs | kernel hrs | overhead % | note |
|---|---|---|---|---|
| 2026-07-06 | _builder to record_ | _builder to record_ | — | FK1: schema extraction (kernel), adapter+pin+mapping instrument (overhead) |
