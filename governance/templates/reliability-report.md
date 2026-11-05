# Reliability Report: <Team or organization>, <Period>

> Monthly for teams, quarterly for leadership. Keep it to two pages. Start
> with the summary; details follow. Replace every `<...>`.

## Summary

> Three bullet points: overall state, the biggest risk, and the decision or
> support needed from leadership.

- `<e.g. All Tier 1 services met their SLOs; checkout used 70% of its budget.>`
- `<e.g. Biggest risk: database at 75% storage, migration planned for March.>`
- `<e.g. Ask: approve two weeks of reliability work for the payments team.>`

## SLO attainment

| Service | Tier | SLO | Objective | Achieved | Budget remaining | Policy state | Trend |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<service>` | `<1>` | `<availability>` | `<99.95%>` | `<99.97%>` | `<40%>` | Normal / Restricted / Frozen / Exception | ↑ / → / ↓ |

"Achieved" is measured over the SLO's own window, ending on the report date.

## Incidents

| Severity | Count | Median time to detect | Median time to mitigate |
| --- | --- | --- | --- |
| SEV0 | | | |
| SEV1 | | | |
| SEV2 | | | |
| SEV3 | | — | — |

Notable incidents (link postmortems):

- `<inc-NNNN>`: `<one line>` (`<link>`)

## Postmortem action items

| Opened this period | Closed this period | Overdue | Oldest overdue |
| --- | --- | --- | --- |
| | | | |

## Accepted risks (from production readiness reviews)

| Service | Risk | Owner | Due | Status |
| --- | --- | --- | --- | --- |
| | | | | |

## Operational load

| Metric | This period | Previous period |
| --- | --- | --- |
| Pages per on-call shift | | |
| Out-of-hours pages | | |
| Estimated toil (hours of manual operational work) | | |

## Recovery readiness

| Service | Last restore test | Result | Restore time vs RTO | Last DR exercise |
| --- | --- | --- | --- | --- |
| | | | | |

## Planned reliability work next period

| Work item | Reason | Owner |
| --- | --- | --- |
| `<item>` | `<SLO risk / postmortem action / PRR risk>` | `<name>` |
