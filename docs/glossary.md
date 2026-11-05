[Reliability Framework](../README.md) › **Glossary**

# Glossary

Plain-language definitions of the terms used across this framework, in
alphabetical order. Each entry points to where the idea is explained in depth.

[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [I](#i) ·
[K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) ·
[R](#r) · [S](#s) · [T](#t) · [Z](#z)

---

## A

**Alert.** An automatic notification that something needs attention. A *page*
wakes someone up; a *ticket* waits for working hours.
→ [SLOs, step 5](../slo/README.md#step-5-alert-on-burn-rate-not-on-every-error)

**Autoscaling.** Adding or removing copies of a program automatically as
demand changes. → [Kubernetes](../kubernetes/README.md#choosing-an-autoscaler)

**Availability zone.** One or more independent data centers within a cloud
region. Spreading a service across several zones means one building losing
power does not take it down. → [Kubernetes](../kubernetes/README.md#reference-architecture)

## B

**Backup and restore.** Keeping copies of data, and proving they can be put
back. A backup that has never been restored is a hope, not a backup.
→ [Database reliability](../database/README.md#2-backups-and-recovery)

**Blameless postmortem.** A written review after an incident that asks how
the system allowed it to happen, not who to blame.
→ [Incident response](../incident-response/README.md#blameless-postmortems)

**Blue/green.** Running a new version of a whole environment ("green") next to
the current one ("blue") and moving users across gradually.
→ [Kubernetes](../kubernetes/README.md#upgrading-and-migrating-safely)

**Burn rate.** How fast the error budget is being used up. A burn rate of 1
uses exactly the whole budget by the end of the period.
→ [SLOs](../slo/README.md#key-terms)

## C

**Canary deployment.** Releasing a new version to a small share of users
first, comparing it automatically with the current version, and only then
releasing it to everyone. Named after the canaries once used to detect gas in
mines. → [Safe delivery](../safe-delivery/README.md#2-canary-deployments)

**CAST.** Causal Analysis based on System Theory: a method for analysing
serious incidents by looking at how the system's controls failed, rather than
for a single root cause.
→ [Incident response](../incident-response/README.md#cast-deeper-analysis-for-major-incidents)

**Cloud.** Computing power rented from a provider such as Amazon Web Services,
Google Cloud or Microsoft Azure, instead of owning the servers.

**Cluster.** A group of machines managed together as one system, usually by
Kubernetes. → [Kubernetes](../kubernetes/)

## D

**Dashboard.** A screen of graphs showing how a service is doing right now.
→ [Observability](../observability/README.md#4-dashboards)

**Dead-letter queue (DLQ).** A holding area for messages that could not be
processed after several attempts, so they are kept for inspection instead of
lost. → [Event-driven systems](../event-driven/README.md#3-retry-with-backoff-then-park-the-message)

**Deployment.** Putting a new version of software into use.

**Disaster recovery (DR).** The plan and practice for restoring service after
a major failure, such as losing a whole data center.
→ [Kubernetes](../kubernetes/README.md#disaster-recovery)

## E

**Error budget.** The amount of failure an SLO allows. With a 99.9% target,
0.1% of requests may fail. While budget remains, teams can move fast; when it
runs out, reliability work comes first. → [SLOs](../slo/README.md#key-terms)

**Event-driven system.** Software made of services that communicate by
sending messages ("order placed", "payment received") through queues.
→ [Event-driven systems](../event-driven/)

## F

**Failover.** Switching automatically to a standby copy when the main one
fails. → [Database reliability](../database/README.md#1-availability-design)

**Feature flag.** A switch that turns a feature on or off without releasing
new software. → [Safe delivery](../safe-delivery/README.md#2-canary-deployments)

## I

**Idempotent.** An operation that has the same effect whether it runs once or
twice, so a repeated message does no harm, such as charging a card twice.
→ [Event-driven systems](../event-driven/README.md#1-assume-at-least-once-delivery-make-consumers-idempotent)

**Incident.** An unplanned event that harms, or threatens to harm, the people
using a service. → [Incident response](../incident-response/)

**Incident commander (IC).** The person in charge during an incident. They
coordinate; they do not do the fixing themselves.
→ [Incident response](../incident-response/README.md#roles)

## K

**Kubernetes.** The most widely used open-source system for running software
across many machines. It restarts failed programs and spreads work around.
→ [Kubernetes](../kubernetes/)

## L

**Latency.** How long a response takes. Usually measured in milliseconds.

**Load balancer.** A component that spreads incoming requests across many
copies of a service and avoids unhealthy ones.

**Logs.** Written records of individual events inside a program, used to
diagnose problems. → [Observability](../observability/README.md#2-logs)

## M

**Metrics.** Numbers measured over time, such as requests per second or error
rate. Cheap to collect, and the basis for dashboards and alerts.
→ [Observability](../observability/README.md#1-metrics)

**Migration (database).** A change to the structure of a database, such as
adding a column. → [Database reliability](../database/README.md#3-safe-schema-changes)

## N

**Node.** One machine (real or virtual) in a cluster.

## O

**Observability.** How well a team can tell, from the outside, what a system
is doing and why. → [Observability](../observability/)

**On-call.** The engineer responsible for responding to alerts during a shift,
including at night. → [Incident response](../incident-response/README.md#on-call)

**OpenTelemetry.** The open, vendor-neutral standard for collecting metrics,
logs and traces from software.
→ [Observability](../observability/README.md#opentelemetry-by-default)

**Outage.** A period when a service does not work for its users.

## P

**Page.** An urgent alert that notifies the on-call engineer immediately, day
or night.

**Pod.** The smallest unit Kubernetes runs: one copy of a program, with what
it needs to run.

**Production.** The live environment real users depend on.

**Production readiness review (PRR).** A checklist review a service must pass
before real users rely on it.
→ [Governance](../governance/README.md#2-production-readiness-review)

**Prometheus.** A widely used open-source monitoring system that collects
metrics and evaluates alert rules.

## Q

**Queue.** A waiting line for messages between services, so the sender and
receiver can work at different speeds.
→ [Event-driven systems](../event-driven/)

## R

**Replica.** One of several identical copies of a program or database.

**Rollback.** Undoing a change by returning to the previous version.
→ [Safe delivery](../safe-delivery/README.md#4-rollback)

**RPO and RTO.** Recovery Point Objective: how much recent data may be lost
in a disaster. Recovery Time Objective: how long recovery may take.
→ [Kubernetes](../kubernetes/README.md#disaster-recovery)

**Runbook.** Step-by-step instructions for responding to a specific alert or
failure. → [Incident response](../incident-response/README.md#runbooks)

## S

**Severity (SEV0 to SEV3).** How bad an incident is for users. SEV0 is the
most serious. → [Incident response](../incident-response/README.md#severity-levels)

**Service.** A piece of software that does one job for users or for other
software, such as "checkout" or "sign-in".

**Site reliability engineering (SRE).** The discipline of keeping software
services dependable by treating operations as an engineering problem: setting
measurable targets, automating, and learning from failure. Started at Google
in 2003. → [README](../README.md#what-is-site-reliability-engineering)

**SLA.** Service Level Agreement: a contract promising a level of service,
usually with penalties if it is missed. → [SLOs](../slo/README.md#key-terms)

**SLI.** Service Level Indicator: the measurement behind an SLO, such as the
share of logins that succeed. → [SLOs](../slo/README.md#key-terms)

**SLO.** Service Level Objective: a measurable target for how reliable a
service must be, such as "99.9% of logins succeed".
→ [SLOs](../slo/)

**Spot instance.** Spare cloud capacity rented cheaply, which the provider can
take back at short notice. → [Kubernetes](../kubernetes/README.md#workload-configuration-checklist)

**Staging.** A copy of production where changes are tested before real users
see them. → [Safe delivery](../safe-delivery/README.md#1-environments)

## T

**Tier (service tier).** How critical a service is, which decides how much
rigor it needs. → [Governance](../governance/README.md#1-service-tiers)

**Traces.** Records that follow one request through every service it touches,
showing where time was spent or where it failed.
→ [Observability](../observability/README.md#3-traces)

## Z

**Zone.** See *availability zone*.

---

[← Back to the overview](../README.md)
