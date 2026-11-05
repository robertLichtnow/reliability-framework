# Reliability Governance

How an organization makes reliability a routine, measurable part of how it
builds software, rather than something addressed only after an outage.

## Summary for non-engineers

Good practices only help if they are applied consistently. Governance is the
set of lightweight checkpoints and reports that make sure every important
service meets the reliability standard before it launches, keeps meeting it
afterwards, and that leadership can see the state of reliability at a glance.
It ties the other modules of this framework together.

## The three checkpoints

| Checkpoint | When | Output |
| --- | --- | --- |
| **Production readiness review (PRR)** | Before a new service or major feature serves real users | Completed [PRR checklist](templates/production-readiness-review.md) with sign-off |
| **Change management** | Every change to production | Reviewed, tested, reversible changes, recorded on dashboards |
| **Reliability review** | Monthly per team; quarterly for leadership | [Reliability report](templates/reliability-report.md) |

## 1. Service tiers

Not every service needs the same rigor. Classify each service so effort goes
where impact is highest.

| Tier | Definition | Requirements |
| --- | --- | --- |
| **Tier 1: Critical** | Outage stops core user journeys, revenue, or affects safety or legal obligations | Full PRR; SLOs with error budget policy; 24/7 on-call; multi-zone; DR tested twice a year |
| **Tier 2: Important** | Outage degrades key features; workarounds exist | PRR; SLOs; business-hours on-call with escalation; multi-zone |
| **Tier 3: Supporting** | Internal tools, batch jobs with slack | Lightweight PRR; basic monitoring and runbooks |

## 2. Production readiness review

A structured review, ideally led by an engineer from outside the owning team,
covering the areas of this framework:

1. **SLOs and error budget policy** ([SLO module](../slo/))
2. **Observability** ([standard](../observability/))
3. **Incident readiness**: on-call, runbooks ([incident response](../incident-response/))
4. **Architecture and capacity**: redundancy, scaling, load tests ([Kubernetes](../kubernetes/))
5. **Data**: backups, restore tests, migrations ([database](../database/))
6. **Asynchronous flows** ([event-driven](../event-driven/))
7. **Security and compliance**
8. **Deployment and rollback**

Items not met are recorded as risks with an owner and a date, and explicitly
accepted by the service owner and an engineering leader. The goal is informed
decisions, not a gate that blocks everything.

## 3. Change management

- All production changes go through version control and peer review,
  including infrastructure and configuration.
- Automated tests and policy checks run before deployment.
- **Progressive delivery**: canary or staged rollout, with automatic rollback
  when error rates or SLO burn rates rise.
- **Feature flags** separate deploying code from releasing features.
- Higher-risk changes (database migrations, network, identity, cluster
  upgrades) require a written plan with a tested rollback.
- Change freezes around known peak periods, with an exception process.
- The error budget policy decides how much risk is acceptable at any time.

## 4. Reliability reporting

Each team reviews its reliability monthly; leadership reviews a summary
quarterly. The [report template](templates/reliability-report.md) covers:

- SLO attainment and error budget remaining, per Tier 1 and Tier 2 service
- Incidents by severity, time to detect and time to mitigate
- Postmortem action items: opened, closed, overdue
- PRR risks accepted and their status
- Toil: repetitive manual operational work, and plans to automate it
- On-call load: pages per shift, out-of-hours pages

## 5. Roles

| Role | Responsibility |
| --- | --- |
| Service owner (team) | Meets the standard for its tier; owns SLOs, runbooks, on-call |
| Reliability / SRE function | Maintains this framework, runs PRRs, coaches teams, builds shared tooling |
| Engineering leadership | Sets tiers, accepts risks, enforces the error budget policy, funds reliability work |
| Product leadership | Agrees SLOs and the error budget policy; balances features against reliability |

## Adoption path

| Phase | Duration | Focus |
| --- | --- | --- |
| 1. Baseline | Month 1 | Tier all services; define SLOs for Tier 1; standard dashboards |
| 2. Respond | Months 2 to 3 | Incident process, runbooks for every paging alert, blameless postmortems |
| 3. Prevent | Months 4 to 6 | PRRs for new services; progressive delivery; backup restore testing |
| 4. Sustain | Ongoing | Monthly reliability reviews; error budget policy enforced; framework updated from lessons learned |
