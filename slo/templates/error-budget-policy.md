# Error Budget Policy: <Service or organization>

> An SLO only changes behavior if everyone agrees in advance what happens when
> it is missed. Adapt the thresholds below, then get sign-off.

| Field | Value |
| --- | --- |
| Applies to | `<services>` |
| Approved by | `<engineering lead>`, `<product lead>`, `<executive sponsor>` |
| Effective from | `<YYYY-MM-DD>` |

## Purpose

Balance the speed of delivering new features with the reliability users
expect. The error budget is the shared, objective measure both sides use.

## Policy

| Budget remaining (current window) | What happens |
| --- | --- |
| More than 50% | Normal operations. Releases proceed as usual. |
| 25% to 50% | Owning team reviews recent incidents and prioritizes the top reliability fix in the next cycle. |
| Above 0% to 25% | Only low-risk releases. No database migrations, cluster upgrades or other higher-risk changes unless they improve reliability. Reliability work takes priority over new features. |
| Exhausted | Feature releases stop, except urgent security and data-integrity fixes, until the SLO is met again over the rolling window or leadership grants a documented exception. |

## Single large incidents

Any incident that consumes more than 20% of the budget on its own requires a
[postmortem](../../incident-response/templates/postmortem.md), completed within five business days, with at least one
tracked action item to prevent recurrence.

## Exceptions

- Failures caused by a dependency still count in this service's SLI, because
  users were affected. If the dependency's owner is already fixing it under
  their own error budget policy, this service's release freeze may be waived.
  Record the decision in the change log.
- Planned maintenance announced to users at least `<N>` days in advance
  `<does / does not>` count against the budget.
- Leadership may grant an exception in writing. Exceptions are recorded in the
  change log below.

## Escalation

Disagreements about budget calculations or this policy go to `<role>`, who
decides within two business days.

## Review

This policy is reviewed every `<quarter>`.

## Change log

| Date | Change | Approved by |
| --- | --- | --- |
| `<YYYY-MM-DD>` | Initial version | `<name>` |
