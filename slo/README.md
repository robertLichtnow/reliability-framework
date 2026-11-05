[Reliability Framework](../README.md) › Module 1 of 8

# Service Level Objectives

This guide walks through creating SLOs for one service. Plan for about two
hours with the people who build, run and own the service.

*For engineers, product owners and managers · About 5 minutes to read · New to a term? See the [glossary](../docs/glossary.md).*

> [!NOTE]
> **In plain language.** A service team agrees on a few numbers that describe "working well" from the
> user's point of view, measures them automatically, and sets a rule for what to
> do when those numbers slip. The result is a short document (one or two pages)
> and a configuration file that monitoring systems read, which turns the
> numbers into automatic alerts.

## On this page

- [Key terms](#key-terms)
- [Step 1: Identify the users and their critical journeys](#step-1-identify-the-users-and-their-critical-journeys)
- [Step 2: Choose indicators (SLIs)](#step-2-choose-indicators-slis)
- [Step 3: Set targets](#step-3-set-targets)
- [Step 4: Write it down](#step-4-write-it-down)
- [Step 5: Alert on burn rate, not on every error](#step-5-alert-on-burn-rate-not-on-every-error)
- [Step 6: Agree on the error budget policy](#step-6-agree-on-the-error-budget-policy)
- [Step 7: Review regularly](#step-7-review-regularly)

## Key terms

| Term | Meaning | Example |
| --- | --- | --- |
| **SLI** (Service Level Indicator) | A measurement of user experience, expressed as a ratio of good events to valid events (the events that count, for example excluding health checks) | Successful logins ÷ all login attempts |
| **SLO** (Service Level Objective) | The target for an SLI over a time window | 99.9% over 30 days |
| **SLA** (Service Level Agreement) | A contract with customers, usually with financial penalties. Should be looser than the SLO | 99.5% or credits are paid |
| **Error budget** | The amount of failure the SLO allows: `1 − SLO` | 0.1% of requests, equal to about 43 minutes of complete outage per 30 days |
| **Burn rate** | How fast the error budget is being used. A burn rate of 1 uses the whole budget exactly at the end of the window | Burn rate 14.4 empties a 30-day budget in about 2 days |

## Step 1: Identify the users and their critical journeys

List who depends on the service and the two to five things they must be able
to do. Ignore internal details; focus on what a user would notice.

Examples: "a customer completes checkout", "an employee signs in",
"a partner system receives a webhook".

## Step 2: Choose indicators (SLIs)

For each journey pick one or two indicators. Most needs are covered by four
kinds:

| Kind | Question it answers | Good event |
| --- | --- | --- |
| Availability | Did it work? | Request returned a non-error response |
| Latency | Was it fast enough? | Response returned within a threshold (e.g. 300 ms) |
| Freshness | Is the data current? | Data updated within N minutes |
| Correctness | Was the result right? | Output passed validation |

Always define an SLI as **good events ÷ valid events**, measured as close to
the user as possible (load balancer or client, not deep inside the system).

## Step 3: Set targets

- Start from what the service achieves today, then adjust to what users need.
- Do not aim for 100%. It is impossible and it freezes all change.
- Each extra "nine" costs roughly ten times more effort:

| Target | Allowed failure per 30 days (as complete outage) |
| --- | --- |
| 99% | 7 hours 12 minutes |
| 99.5% | 3 hours 36 minutes |
| 99.9% | 43 minutes 12 seconds |
| 99.95% | 21 minutes 36 seconds |
| 99.99% | 4 minutes 19 seconds |
| 99.999% | 26 seconds |

## Step 4: Write it down

Fill in [`templates/slo-document.md`](templates/slo-document.md) for people
and [`templates/slo.yaml`](templates/slo.yaml) for machines.

## Step 5: Alert on burn rate, not on every error

Paging an engineer for each error causes alert fatigue. Instead, alert when
the error budget is being consumed too quickly. The tool in
[`../tools/slo_tool.py`](../tools/slo_tool.py) generates these alerts using
the multi-window, multi-burn-rate method from *The Site Reliability Workbook*:

| Severity | Budget consumed | Long window | Short window | Burn rate (30-day SLO) |
| --- | --- | --- | --- | --- |
| Page | 2% | 1 hour | 5 minutes | 14.4 |
| Page | 5% | 6 hours | 30 minutes | 6 |
| Ticket | 10% | 3 days | 6 hours | 1 |

The short window makes the alert stop quickly once the problem is fixed.

In everyday terms: someone is paged only if, at the current failure rate, the
whole month's allowance would be gone in about 2 days (fast burn) or 5 days
(medium burn). A slower leak becomes a ticket for working hours.

The table assumes a 30-day window. For other windows (7 to 90 days) the tool
scales the burn rates, never below 1, and `slo_tool.py budget` prints the
actual thresholds.

**What burn-rate alerts cannot see**

- **Missing data.** If the service crashes and stops reporting metrics, there
  is nothing to compute. Measure at the load balancer where possible, and add
  an alert on missing data (for example `absent(<total query>)` or the scrape
  target being down).
- **Very low traffic.** With a handful of requests per hour, one error can
  page. Require a minimum request rate before paging, group small services
  together, or add synthetic traffic.

**Also generated:** a recording rule for the error ratio over the whole SLO
window and `slo:error_budget_remaining:ratio`, used by dashboards, the error
budget policy and reliability reports. Prometheus keeps 15 days of data by
default, so a 30-day window needs at least 30 days of retention or long-term
storage. Both page alerts can fire together during a fast burn; group them in
Alertmanager by `service` and `slo` so the on-call engineer gets one
notification.

Every generated alert links to the `runbook_url` and `dashboard_url` set in
`slo.yaml`. The example includes [promtool unit tests](examples/checkout-api/alerts-test.yaml)
that prove the alerts fire during an outage and stay quiet when healthy.

## Step 6: Agree on the error budget policy

Copy [`templates/error-budget-policy.md`](templates/error-budget-policy.md)
and get sign-off from engineering, product and leadership. Without an agreed
consequence, an SLO is only a dashboard.

## Step 7: Review regularly

Review each SLO monthly for the first quarter, then quarterly. Tighten targets
that are always met with room to spare; loosen ones that users do not notice
being missed.

---

| Previous | Overview | Next |
| :--- | :---: | ---: |
|  | [All modules](../README.md#the-eight-modules) | [2. Observability →](../observability/) |
