# Runbook: <Alert or failure name>

> One runbook per alert or known failure mode. Write it for an engineer who
> has never seen this service and has just been woken up. Replace every
> `<...>` placeholder.

| Field | Value |
| --- | --- |
| Service | `<service>` |
| Alert name(s) | `<e.g. SLOBurnRatePage for checkout-api/availability>` |
| Owner | `<team>` |
| Default severity | `<SEV0 / SEV1 / SEV2>` |
| Last tested | `<YYYY-MM-DD>` |
| Last reviewed | `<YYYY-MM-DD>` |

## What this alert means

> One or two sentences in plain language: what users are experiencing.

`<e.g. Shoppers are seeing errors when paying. At the current rate the
monthly error budget will be used up within two days.>`

## 1. Confirm user impact (2 minutes)

- Dashboard: `<link>`
- Check: `<which graph, what "bad" looks like>`
- If there is no user impact, this may be a monitoring problem. Go to
  [False alarms](#false-alarms).

## 2. Declare and communicate

- If impact is confirmed, declare an incident at severity `<level>` and
  follow the [incident process](../README.md#lifecycle).
- Post the first update using the
  [status update template](status-update.md).

## 3. Mitigate

> Ordered from safest and fastest to most disruptive. Each step has a command
> or link, the expected result, and how long to wait before moving on.

| # | Action | Command or link | Expected result | Wait |
| --- | --- | --- | --- | --- |
| 1 | Was there a change in the last 2 hours? Roll it back. | `<deploy history link / rollback command>` | Error rate falls within 5 minutes | 5 min |
| 2 | Is one zone or cluster unhealthy? Shift traffic away. | `<command>` | Errors stop on the healthy side | 5 min |
| 3 | Is the service saturated? Scale out. | `<command>` | CPU / queue depth fall | 10 min |
| 4 | Is a dependency failing? Check its status and escalate. | `<dependency dashboard / contact>` | Owner engaged | — |
| 5 | `<feature flag / degrade gracefully>` | `<command>` | `<result>` | 5 min |

## 4. Diagnose (after impact is mitigated)

- Logs: `<query link>`
- Traces: `<query link>`
- Common causes seen before:
  - `<cause>`: `<how to recognize it>`, `<fix>`

## 5. Verify recovery

- SLIs back within objective for at least `<30>` minutes on `<dashboard>`.
- Error budget dashboard: `<link>`.
- The incident commander declares resolution.

## Escalation

| When | Who | How |
| --- | --- | --- |
| No progress after 30 minutes | `<secondary on-call>` | `<pager / phone>` |
| Data loss or security concern | `<security on-call>` | `<pager>` |
| Dependency outage | `<dependency owner>` | `<channel / pager>` |

## False alarms

If the alert fired without user impact, open a ticket against `<team>` to fix
the alert. Record the date here so repeated false alarms are visible.

## Change log

| Date | Change | Author |
| --- | --- | --- |
| `<YYYY-MM-DD>` | Initial version | `<name>` |
