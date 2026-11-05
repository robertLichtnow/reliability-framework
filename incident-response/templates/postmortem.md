# Postmortem: <Short title>

> Blameless: describe what the system and process allowed, not who made a
> mistake. Write facts, with timestamps in UTC. Replace every `<...>`.

| Field | Value |
| --- | --- |
| Incident ID | `<inc-NNNN>` |
| Severity | `<SEV0 / SEV1 / SEV2>` |
| Date | `<YYYY-MM-DD>` |
| Duration of user impact | `<hh:mm>` |
| Services affected | `<services>` |
| Error budget consumed | `<% of the window's budget, per SLO>` |
| Detected by | Alert / customer / employee |
| Incident commander | `<name>` |
| CAST analysis | `<link, if done>` |
| Authors | `<names>` |
| Status | Draft / In review / Final |

## Summary

> Three to five sentences a non-engineer can follow: what users experienced,
> for how long, why, and what is being done so it does not happen again.

## Impact

- Users affected: `<number or percentage, and which users>`
- What they experienced: `<errors, slowness, data delay>`
- Business impact: `<orders lost, SLA credits, support tickets>`
- Data impact: `<none / delayed / lost / exposed>`

## Timeline (UTC)

| Time | Event |
| --- | --- |
| `<hh:mm>` | `<Triggering change or event>` |
| `<hh:mm>` | User impact begins |
| `<hh:mm>` | First alert fires / first report received |
| `<hh:mm>` | Incident declared, IC assigned |
| `<hh:mm>` | Mitigation applied: `<what>` |
| `<hh:mm>` | User impact ends |
| `<hh:mm>` | Incident resolved |

Time to detect: `<mm>` · Time to mitigate: `<mm>`

## Contributing factors

> List several. Consider technology, process, tooling, documentation and
> organizational factors. For SEV0 or repeat incidents, or if this list
> stops at "human error", also complete a [CAST analysis](cast-analysis.md).

1. `<factor>`
2. `<factor>`

## What went well

- `<e.g. Rollback completed in 4 minutes>`

## What was difficult

- `<e.g. Runbook link in the alert was out of date>`

## AI assistance (if used)

- What the agent found or suggested, and whether it was correct: `<...>`
- Effect on time to mitigate: `<faster / no change / slower>`

## Where we got lucky

- `<e.g. Happened during business hours with experts available>`

## Action items

> Each item prevents recurrence, improves detection, or speeds up mitigation.
> Every item has an owner, a due date and a ticket.

| # | Action | Type | Owner | Due | Ticket |
| --- | --- | --- | --- | --- | --- |
| 1 | `<action>` | Prevent / Detect / Mitigate | `<name>` | `<date>` | `<link>` |

## Supporting information

- Incident channel: `<link>`
- Dashboards and graphs: `<links or screenshots>`
- Related postmortems: `<links>`
