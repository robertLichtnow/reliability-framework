# Incident Response

How to detect, coordinate, resolve and learn from outages in a consistent way.

## Summary for non-engineers

When an online service breaks, every minute counts. Teams that improvise lose
time deciding who is in charge, who tells customers and what to try first.
This module gives a team a shared playbook: clear severity levels, defined
roles, step-by-step runbooks for known failures, and a blameless review after
every serious incident so the same problem does not happen twice.

## Contents

| File | Purpose |
| --- | --- |
| This guide | Severity levels, roles, lifecycle, communication rules |
| [`templates/runbook.md`](templates/runbook.md) | Step-by-step instructions for responding to one specific alert or failure |
| [`templates/postmortem.md`](templates/postmortem.md) | Blameless post-incident review |
| [`templates/status-update.md`](templates/status-update.md) | Ready-to-use wording for internal and customer updates |

## Severity levels

Severity is based on **user impact**, never on how hard the problem is to fix.
When in doubt, choose the higher severity; downgrading later is cheap.

| Level | Definition | Examples | Response |
| --- | --- | --- | --- |
| **SEV0** | Critical service unavailable or data at risk for many users | Nobody can sign in; data loss or exposure; security breach | Page immediately, 24/7. Incident commander assigned within 5 minutes. Customer updates every 30 minutes. Executive notified. |
| **SEV1** | Major feature degraded, or a critical service down for a subset of users | Checkout failing for one region; error rate 5x normal | Page immediately, 24/7. Updates every 60 minutes. |
| **SEV2** | Minor degradation with a workaround | Slow reports; one non-critical integration failing | Handled in business hours. Ticket tracked to resolution. |
| **SEV3** | No current user impact, but risk if left alone | Backup job failed once; disk at 80% | Ticket in the owning team's backlog. |

SEV0 and SEV1 always get a postmortem. SEV2 gets one if it repeats or reveals
a systemic gap.

## Roles

For SEV0 and SEV1, these roles are assigned explicitly and announced in the
incident channel. One person may hold several roles in a small team, but the
incident commander should not also be the person typing the fix.

| Role | Responsibility |
| --- | --- |
| **Incident commander (IC)** | Owns the incident end to end. Sets priorities, assigns tasks, decides when to escalate and when it is resolved. Does not debug. |
| **Operations lead** | Investigates and applies changes. Announces every action before taking it. |
| **Communications lead** | Posts internal and customer updates on schedule using the status update template. |
| **Scribe** | Keeps a timestamped log of observations, decisions and actions. The log becomes the postmortem timeline. This role can be filled, or assisted, by an AI transcription tool that records the incident call and channel and posts regular summaries, so people joining late or following along catch up without interrupting responders. A human still checks the summaries for accuracy. |
| **Subject matter experts** | Pulled in by the IC as needed. |

## Lifecycle

1. **Detect.** An SLO burn-rate alert, a monitor or a user report.
   Prefer alerts based on user impact (see the [SLO module](../slo/)).
2. **Declare.** Anyone may declare an incident. Open a dedicated channel and
   name it `inc-YYYYMMDD-short-description`. Set a severity.
3. **Assemble.** Assign the IC and other roles. Post the first status update
   within 15 minutes for SEV0 and SEV1.
4. **Mitigate first, diagnose later.** Restore service before finding the root
   cause. The fastest mitigations, in order of preference:
   - roll back the most recent change (deploy, configuration, feature flag);
   - shift traffic away from the failing zone, region or cluster;
   - add capacity;
   - turn off the failing feature;
   - restore from backup, only when data is affected.
5. **Resolve.** The IC declares resolution once the SLIs are back within
   objective and stable for an agreed period (for example 30 minutes).
6. **Learn.** Schedule the postmortem within five business days. Track every
   action item to completion.

## Communication rules

- One channel per incident. Side conversations are moved into it.
- Updates follow a fixed format: impact, current status, next step, time of
  the next update. See [`templates/status-update.md`](templates/status-update.md).
- Customer-facing updates state facts and impact, not speculation about
  causes.
- If nothing has changed, post an update saying so. Silence causes more alarm
  than bad news.

## Runbooks

Every alert that can page a human must link to a runbook. A good runbook:

- can be followed by an engineer who has never seen the service, at 3 a.m.;
- starts with how to confirm user impact and how to mitigate, before
  diagnosis;
- contains copy-paste commands and links to dashboards, not prose
  descriptions of them;
- is reviewed after each use and at least every six months.

Alerts without a clear action should not page anyone; turn them into tickets
or remove them.

## Blameless postmortems

The goal is to understand how the system, including its tools, processes and
incentives, allowed the incident to happen. People are not the root cause:
if one person's mistake can take down production, the safeguards are what
failed.

- Write the timeline from the scribe's log.
- Ask "how did this make sense at the time?" rather than "who did this?".
- Look for several contributing factors, not a single root cause.
- Each action item has an owner, a due date and a ticket. Prefer actions that
  prevent a whole class of failure over ones that fix only this instance.
- Share postmortems widely. Other teams learn from them too.

## Measuring the practice

Track these monthly to show whether incident response is improving:

| Metric | Meaning |
| --- | --- |
| Time to detect | Start of user impact to first alert or report |
| Time to mitigate | Start of user impact to impact ending |
| Incidents by severity | Count of SEV0 to SEV3 |
| Error budget consumed per incident | Links incidents to SLOs |
| Postmortem action items closed on time | Whether lessons are actually applied |
| Repeat incidents | Incidents with the same contributing factor as a previous one |
