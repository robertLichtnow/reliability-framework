# CAST Analysis: <Incident ID and title>

> CAST (Causal Analysis based on System Theory) was developed by Nancy
> Leveson at MIT as part of the STAMP accident model. Instead of looking for a
> single root cause, it treats an incident as a failure of **control**: the
> people, automation and processes meant to keep the system safe did not
> enforce the right constraints, usually because the information they had
> did not match reality.
>
> Use it for SEV0 incidents, repeat incidents, and any incident where the
> standard postmortem feels like it stopped at "human error". Attach the
> result to the [postmortem](postmortem.md). Replace every `<...>`.

| Field | Value |
| --- | --- |
| Incident | `<inc-NNNN>` |
| Postmortem | `<link>` |
| Facilitator | `<name, ideally not from the owning team>` |
| Participants | `<names>` |

## 1. Basic information

**Loss:** what unacceptable outcome happened?
`<e.g. Customers could not complete payments for 47 minutes.>`

**Hazard:** what system state made the loss possible?
`<e.g. All checkout pods depended on a configuration value with no validation.>`

**System-level constraint that was violated:**
`<e.g. Configuration changes must not reduce checkout capacity below demand.>`

**Proximate events** (short, factual, from the postmortem timeline):

1. `<event>`
2. `<event>`

## 2. Control structure

> Draw (as an image, or a list) who and what controls the part of the system
> involved, from leadership down to automation and infrastructure. For each
> link, note the **control actions** sent down and the **feedback** sent
> back up.

| Controller | Controls | Control actions | Feedback it receives |
| --- | --- | --- | --- |
| `<Engineering leadership>` | `<Team priorities>` | `<Roadmap, staffing>` | `<Reliability reports>` |
| `<Owning team>` | `<Service, deploys>` | `<Code, config changes>` | `<Dashboards, alerts>` |
| `<CI/CD pipeline>` | `<Deployments>` | `<Rollout, rollback>` | `<Health checks, canary analysis>` |
| `<Kubernetes / autoscaler>` | `<Pods, nodes>` | `<Schedule, scale, evict>` | `<Metrics, probes>` |

## 3. Analysis of each controller

> For every controller involved (human or automated), answer the questions
> below. The goal is to explain why its actions **made sense at the time**,
> given what it knew.

### `<Controller name>`

| Question | Answer |
| --- | --- |
| Responsibilities related to the hazard | |
| Unsafe control actions (what it did, didn't do, did too early, too late, or for too long) | |
| Process model: what it believed about the system at the time | |
| Why that belief was wrong or incomplete (missing, delayed or misleading feedback) | |
| Context: pressures, incentives, tooling, workload, ambiguity | |

> Repeat for each controller.

## 4. System-wide factors

| Factor | Finding |
| --- | --- |
| Communication and coordination between controllers | |
| Feedback and observability gaps | |
| Changes over time that eroded safety margins (drift) | |
| Organizational pressures (deadlines, staffing, incentives) | |
| Safety and reliability culture | |
| Gaps in standards, runbooks or tooling | |

## 5. Recommendations

> Prefer changes to the **control structure** (better feedback, enforced
> constraints, clearer responsibilities) over "be more careful". Each
> recommendation has an owner and is tracked like any postmortem action item.

| # | Recommendation | Controller / link it fixes | Owner | Due | Ticket |
| --- | --- | --- | --- | --- | --- |
| 1 | `<e.g. Validate config schema in CI and at load time>` | `<CI/CD pipeline>` | | | |

## Reference

Nancy G. Leveson, *CAST Handbook: How to Learn More from Incidents and
Accidents* (MIT, 2019), and *Engineering a Safer World* (MIT Press, 2011).
