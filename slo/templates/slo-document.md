# SLO: <Service name>

> Replace every `<...>` placeholder. Delete guidance lines (starting with `>`)
> once complete. Keep this document to one or two pages.

| Field | Value |
| --- | --- |
| Service | `<name>` |
| Owner (team) | `<team>` |
| Document approvers | `<engineering lead>`, `<product owner>` |
| Status | Draft / Approved |
| Last reviewed | `<YYYY-MM-DD>` |
| Next review | `<YYYY-MM-DD>` |
| Machine-readable file | `<path to slo.yaml>` |

## 1. Summary

> Two or three sentences a non-engineer can read: what the service does, who
> relies on it, and the headline target.

`<Service>` lets `<users>` `<do what>`. We commit that `<headline objective>`.

## 2. Users and critical journeys

| Journey | Users | Why it matters |
| --- | --- | --- |
| `<e.g. Sign in>` | `<e.g. end customers>` | `<impact if it fails>` |

## 3. Service level indicators

> Define each SLI as good events divided by valid events. State where it is
> measured and what is excluded.

| SLI | Good event | Valid event | Measured at | Exclusions |
| --- | --- | --- | --- | --- |
| `<availability>` | `<non-5xx response>` | `<all requests>` | `<load balancer>` | `<health checks>` |
| `<latency>` | `<response under 300 ms>` | `<all successful requests>` | `<load balancer>` | `<none>` |

## 4. Objectives

| SLI | Target | Window | Error budget |
| --- | --- | --- | --- |
| `<availability>` | `<99.9%>` | `<30 days rolling>` | `<43m 12s>` |

> Calculate budgets with `python tools/slo_tool.py budget <slo.yaml>`.

## 5. Rationale

> Why these targets? Cite current performance, user expectations, contracts
> (SLAs) and dependencies. A target should never be stricter than the
> services it depends on can support.

## 6. Alerting

| Alert | Condition | Severity | Responder |
| --- | --- | --- | --- |
| Fast burn | Burn rate ≥ 14.4 over 1h and 5m | Page | On-call engineer |
| Medium burn | Burn rate ≥ 6 over 6h and 30m | Page | On-call engineer |
| Slow burn | Burn rate ≥ 1 over 3d and 6h | Ticket | Owning team |

## 7. Error budget policy

This service follows `<link to error budget policy>`.

## 8. Dependencies

| Dependency | Its SLO | Effect if it fails |
| --- | --- | --- |
| `<database>` | `<99.95%>` | `<all writes fail>` |

## 9. Change log

| Date | Change | Approved by |
| --- | --- | --- |
| `<YYYY-MM-DD>` | Initial version | `<name>` |
