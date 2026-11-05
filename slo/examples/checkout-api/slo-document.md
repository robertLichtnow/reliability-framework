# SLO: Checkout API

> A complete example based on a fictional online store. Numbers are
> illustrative. Compare with the blank
> [template](../../templates/slo-document.md).

| Field | Value |
| --- | --- |
| Service | `checkout-api` |
| Owner (team) | Payments Platform |
| Document approvers | Engineering lead, Payments; Product owner, Checkout |
| Status | Approved |
| Last reviewed | 2026-11-05 |
| Next review | 2027-02-05 |
| Machine-readable file | [`slo.yaml`](slo.yaml) |

## 1. Summary

The Checkout API lets shoppers pay for their orders. If it fails, the store
loses sales immediately and customers may be charged without receiving an
order confirmation. We commit that **99.95% of checkout requests succeed and
99% complete in under 0.8 seconds**, measured over every rolling 30 days.

## 2. Users and critical journeys

| Journey | Users | Why it matters |
| --- | --- | --- |
| Place an order and pay | Shoppers on web and mobile | Direct revenue; a failure here is a lost sale |
| Confirm payment to the order system | Warehouse and order systems | A missed confirmation means a paid order is not shipped |

## 3. Service level indicators

| SLI | Good event | Valid event | Measured at | Exclusions |
| --- | --- | --- | --- | --- |
| Availability | Response is not a 5xx server error | All requests to `/v1/checkout*` | Load balancer | Health checks; requests rejected for invalid input (4xx) count as good, because the service behaved correctly |
| Latency | Response sent in under 800 ms | All requests to `/v1/checkout*` | Load balancer | None |
| Payment confirmation | Confirmation delivered to the order system within 60 s | All successful charges | Checkout API event publisher | Test transactions |

## 4. Objectives

| SLI | Target | Window | Error budget |
| --- | --- | --- | --- |
| Availability | 99.95% | 30 days rolling | 0.05%, about 21m 36s of full outage |
| Latency | 99.0% | 30 days rolling | 1% of requests may be slower than 800 ms |
| Payment confirmation | 99.9% | 30 days rolling | 0.1%, about 43m 12s |

Output of `python tools/slo_tool.py budget slo/examples/checkout-api/slo.yaml`:

```
Service: checkout-api   Window: 30 days

SLO                   Objective    Budget    Allowed downtime
availability             99.95%   0.0500%             21m 36s
latency                   99.0%   1.0000%              7h 12m
payment-confirmation      99.9%   0.1000%             43m 12s

Alert thresholds (multi-window, multi-burn-rate):
  page    burn rate >= 14.4 over 1h and 5m (2% of budget in 1h)
  page    burn rate >= 6 over 6h and 30m (5% of budget in 6h)
  ticket  burn rate >= 1 over 3d and 6h (10% of budget in 3d)
```

## 5. Rationale

- Over the last quarter the service achieved 99.97% availability, so 99.95%
  is achievable while leaving room for planned releases.
- The payment provider guarantees 99.99%, and the database runs at 99.99%, so
  dependencies support this target.
- Customer research shows checkout abandonment rises sharply above one second;
  800 ms keeps a safety margin.
- The customer-facing SLA is 99.9%. The internal SLO is stricter so the team
  reacts before any contractual penalty applies.

## 6. Alerting

Generated rules: [`prometheus-rules.yaml`](prometheus-rules.yaml).

| Alert | Condition | Severity | Responder |
| --- | --- | --- | --- |
| Fast burn | Burn rate ≥ 14.4 over 1h and 5m | Page | Payments on-call |
| Medium burn | Burn rate ≥ 6 over 6h and 30m | Page | Payments on-call |
| Slow burn | Burn rate ≥ 1 over 3d and 6h | Ticket | Payments Platform backlog |

## 7. Error budget policy

This service follows the organization's
[error budget policy](../../templates/error-budget-policy.md) with default
thresholds.

## 8. Dependencies

| Dependency | Its SLO | Effect if it fails |
| --- | --- | --- |
| Payment provider API | 99.99% | Charges fail; checkout returns an error |
| Orders database | 99.99% | All checkouts fail |
| Message queue | 99.95% | Payment confirmations are delayed, not lost |

## 9. Change log

| Date | Change | Approved by |
| --- | --- | --- |
| 2026-11-05 | Initial version | Engineering lead, Payments |
