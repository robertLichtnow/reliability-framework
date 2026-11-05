[Reliability Framework](../README.md) › Module 4 of 8

# Safe delivery

How to move a change from a developer's laptop to every user without breaking
the service: a staging environment that acts as a real gate, canary
deployments for critical services, and gradual traffic shifting for large
platform changes.

*For engineers and engineering leads · About 7 minutes to read · New to a term? See the [glossary](../docs/glossary.md).*

> [!NOTE]
> **In plain language.** Most outages start with a change: new code, a new setting, a new version of
> the platform. Safe delivery catches bad changes early, while they affect
> nobody or only a small share of users, and undoes them automatically. A
> change first has to pass a full rehearsal in a copy of production
> (*staging*). Then it reaches users gradually, a small percentage at a time,
> while automated checks compare it against the current version. If anything
> looks worse, it is rolled back before most users ever see it.

## On this page

- [Core principle: unobserved is unproven](#core-principle-unobserved-is-unproven)
- [1. Environments](#1-environments)
- [2. Canary deployments](#2-canary-deployments)
- [3. Large platform changes: gradual traffic shifting](#3-large-platform-changes-gradual-traffic-shifting)
- [4. Rollback](#4-rollback)
- [Checklist](#checklist)

## Core principle: unobserved is unproven

> If something is not being used, or we cannot observe it, we cannot be sure
> it works.

A new server, version or cluster that receives no real traffic emits no
meaningful telemetry. Dashboards look green simply because nothing is
happening. "Deployed and idle" is not the same as "working".

This principle drives every practice in this module:

- **New versions and new clusters earn trust with real traffic**, starting
  with a small percentage and growing only while measurements stay healthy.
  Never switch 100% of traffic to something that has served none.
- **Synthetic checks are a starting point, not proof.** Use them to confirm
  the basics before real users arrive, then rely on real traffic.
- **Standby capacity should carry some live traffic.** A disaster recovery
  cluster or region that sits idle for months will likely fail when it is
  finally needed. Keep it serving a share of traffic, or exercise it on a
  schedule.
- **Rarely used paths need deliberate exercise**: failover, backup restores,
  rollbacks. Practice them so the first real use is not the first use.

## 1. Environments

| Environment | Purpose | Treated as |
| --- | --- | --- |
| Development | Individual and team testing | Disposable |
| **Staging (pre-production)** | Final gate before production; mirrors production configuration | **Production-grade** |
| Production | Real users | Production |

Where reliability is taken seriously, a staging environment is not optional.

**Staging is the first line of defense, so it is held to production
standards:**

- **Always green.** A broken staging environment blocks releases and is fixed
  with the same urgency as a production problem. A staging environment that
  is often broken trains people to ignore it.
- **Same shape as production**: same infrastructure code, same Kubernetes
  version and add-ons, same configuration (scaled down), same deployment
  pipeline. Differences are documented and kept to a minimum. During an
  upgrade, staging deliberately runs the new version first.
- **Monitored and alerted** like production, routed to the owning team during
  business hours.
- **Realistic data and traffic**: anonymized or synthetic data at realistic
  volume, plus continuous synthetic traffic so it is never idle (see the core
  principle).
- **Every production change passes through it first**: application code,
  infrastructure, database migrations, cluster upgrades and add-on upgrades,
  and also configuration, feature-flag and secret changes, which cause many
  of the largest outages. With several clusters or regions, production
  rollouts go in waves with bake time between them, never all at once.

**Gates in staging.** A change is promoted to production only when:

1. Automated unit and integration tests pass.
2. The change is deployed to staging with the same pipeline used for
   production.
3. End-to-end tests of critical user journeys pass against staging.
4. Database migrations ran successfully against realistic data volumes.
5. Staging SLOs and error rates stayed healthy for an agreed soak period.

**Build once, promote the same artifact.** The exact container image tested
in staging is the one deployed to production, identified by its digest.
Never rebuild for production.

## 2. Canary deployments

For Tier 1 (critical) and Tier 2 (important) services (see
[service tiers](../governance/README.md#1-service-tiers)), every production
deployment is a canary:

1. Deploy the new version alongside the current one, receiving no traffic.
2. Send a small share of real traffic to it, for example **1% to 5%**.
3. **Automatically compare** the canary with the current version: error rate,
   latency percentiles, saturation and key business metrics.
4. If the canary is as good as the current version, increase traffic in
   steps (for example 5% → 25% → 50% → 100%), pausing at each step.
5. If it is worse at any step, **roll back automatically** and alert the
   team. Most users never see the problem.

**Guidelines**

- Each step must last long enough, and receive enough traffic, for the
  comparison to be meaningful. A canary that served ten requests proves
  nothing.
- Compare canary against the current version at the same time, not against
  yesterday's numbers; this filters out normal daily variation.
- Judge the canary on its own metrics, labelled by version. The service-wide
  SLO burn rate is only a backstop: at 1% of traffic a canary can fail every
  request while a 99.9% SLO burns at only 10x, below the 14.4x page
  threshold. If the burn rate does reach the page threshold, the rollout
  halts.
- Tooling such as Argo Rollouts or Flagger automates traffic shifting,
  analysis and rollback on Kubernetes, typically using a service mesh or
  ingress controller to split traffic.
- Separate **deploying** code from **releasing** features with feature flags.
  Risky features are turned on gradually and can be turned off instantly
  without a deployment.

Staging and canaries complement each other. Good staging gates catch most
problems before any user is involved; canaries catch what only appears with
real users, real data and real scale.

## 3. Large platform changes: gradual traffic shifting

The same approach applies to infrastructure. A new cluster, region, network
layer or major operator upgrade is introduced as a "green" environment next
to the current "blue" one (see
[High-availability Kubernetes](../kubernetes/README.md#upgrading-and-migrating-safely)):

1. Build green entirely from code and validate it with synthetic traffic.
2. Shift real traffic by percentage (1% → 10% → 50% → 100%), holding at each
   step while SLOs stay healthy. An idle green environment proves nothing.
3. Keep blue ready for rollback until green has run a full business cycle at
   full traffic. Background work, capacity and DNS caching need care while
   both run; see the [Kubernetes migration steps](../kubernetes/README.md#upgrading-and-migrating-safely).

## 4. Rollback

- Rollback is the default response to a bad change, and it must be faster
  than any fix: one command or one click, ideally automatic. With GitOps,
  roll back by reverting the commit or letting the rollout controller abort;
  a manual `kubectl rollout undo` is reverted by the next sync.
- Every deployment must be reversible. Changes that cannot be reversed
  (some database migrations, data deletions) follow the
  expand-and-contract pattern in
  [Database reliability](../database/README.md#3-safe-schema-changes) or get
  explicit sign-off.
- Test rollbacks in staging regularly. An untested rollback is subject to the
  core principle too.

## Checklist

| # | Requirement | Done |
| --- | --- | --- |
| 1 | Staging environment built from the same code and pipeline as production | ☐ |
| 2 | Staging is monitored, kept always green, and broken staging blocks releases | ☐ |
| 3 | Continuous synthetic traffic in staging; critical journeys tested end to end | ☐ |
| 4 | The same artifact (image digest) is promoted from staging to production | ☐ |
| 5 | Canary deployments with automated analysis for Tier 1 and Tier 2 services | ☐ |
| 6 | Automatic rollback on canary failure or SLO burn-rate alert | ☐ |
| 7 | Feature flags for risky features | ☐ |
| 8 | Platform changes rolled out by percentage of traffic, never all at once | ☐ |
| 9 | Standby environments carry live traffic or are exercised on a schedule | ☐ |
| 10 | Rollbacks tested regularly | ☐ |

---

| Previous | Overview | Next |
| :--- | :---: | ---: |
| [← 3. Incident response](../incident-response/) | [All modules](../README.md#the-eight-modules) | [5. High-availability Kubernetes →](../kubernetes/) |
