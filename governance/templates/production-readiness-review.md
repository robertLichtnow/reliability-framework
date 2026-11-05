# Production Readiness Review: <Service>

> Complete before the service serves real users, and again after major
> changes. Mark each item **Yes**, **No** or **N/A**. Every **No** becomes a
> risk in the table at the end. Replace every `<...>`.

| Field | Value |
| --- | --- |
| Service | `<name>` |
| Tier | `<1 / 2 / 3>` |
| Owning team | `<team>` |
| Reviewer (outside the team) | `<name>` |
| Review date | `<YYYY-MM-DD>` |
| Planned launch | `<YYYY-MM-DD>` |

## 1. Service level objectives

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 1.1 | Are critical user journeys documented? | | |
| 1.2 | Are SLOs defined in a [SLO document](../../slo/templates/slo-document.md) and `slo.yaml`? | | |
| 1.3 | Is there an agreed error budget policy? | | |
| 1.4 | Are the SLOs achievable given dependency SLOs? | | |

## 2. Observability

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 2.1 | Does the service meet the [observability checklist](../../observability/README.md#checklist)? | | |
| 2.2 | Is there a standard overview dashboard? | | |
| 2.3 | Are burn-rate alerts in place and tested? | | |

## 3. Incident readiness

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 3.1 | Is there an on-call rotation matching the tier? | | |
| 3.2 | Does every paging alert link to a runbook? | | |
| 3.3 | Have on-call engineers walked through the runbooks? | | |
| 3.4 | Are escalation contacts for dependencies documented? | | |

## 4. Architecture and capacity

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 4.1 | Does the service survive the loss of a node and of a zone? How was this tested? | | |
| 4.2 | Does it meet the [workload checklist](../../kubernetes/README.md#workload-configuration-checklist) (or equivalent)? | | |
| 4.3 | Has it been load-tested to at least 2x expected peak? | | |
| 4.4 | Does it degrade gracefully when a dependency fails (timeouts, circuit breakers, fallbacks)? | | |
| 4.5 | Are single points of failure identified and accepted or removed? | | |
| 4.6 | (Tier 1) Is there a DR plan with RTO and RPO, exercised in the last six months? | | |

## 5. Data

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 5.1 | Does the data layer meet the [database checklist](../../database/README.md#checklist)? | | |
| 5.2 | Has a restore from backup been tested and timed? | | |
| 5.3 | Are RPO and RTO agreed with the business? | | |

## 6. Asynchronous processing (if applicable)

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 6.1 | Does it meet the [event-driven checklist](../../event-driven/README.md#checklist)? | | |

## 7. Security and compliance

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 7.1 | Has a security review or threat model been completed? | | |
| 7.2 | Are secrets managed in a secret store and rotated? | | |
| 7.3 | Is personal or regulated data identified and protected? | | |
| 7.4 | Are dependencies scanned for known vulnerabilities? | | |

## 8. Deployment and rollback

> See the [safe delivery checklist](../../safe-delivery/README.md#checklist).

| # | Question | Answer | Notes |
| --- | --- | --- | --- |
| 8.1 | Is deployment fully automated from version control? | | |
| 8.2 | Does every change pass through a production-grade staging environment first? | | |
| 8.3 | Is every deployment a canary with automated analysis and automatic rollback (Tier 1 and 2)? | | |
| 8.4 | Has a rollback been performed in a test environment? | | |
| 8.5 | Can features be disabled with flags without a deployment? | | |

## Risks and decisions

| # | Item not met | Risk | Mitigation / plan | Owner | Due | Accepted by |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `<item>` | `<impact>` | `<plan>` | `<name>` | `<date>` | `<name>` |

## Sign-off

| Role | Name | Date | Decision |
| --- | --- | --- | --- |
| Service owner | | | Ready / Ready with accepted risks / Not ready |
| Reviewer | | | |
| Engineering leader (Tier 1, or any tier with accepted risks) | | | |
