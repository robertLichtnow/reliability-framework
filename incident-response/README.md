# Incident Response

How to detect, coordinate, resolve and learn from outages in a consistent way.

## Summary for non-engineers

When an online service breaks, every minute counts. Teams that improvise lose
time deciding who is in charge, who tells customers and what to try first.
This module gives a team a shared playbook: clear severity levels, defined
roles, step-by-step runbooks for known failures, and a blameless review after
every serious incident so the same problem is far less likely to happen again.

## Contents

| File | Purpose |
| --- | --- |
| This guide | Severity levels, roles, lifecycle, on-call, AI agents, communication, runbooks, postmortems, CAST, metrics |
| [`templates/runbook.md`](templates/runbook.md) | Step-by-step instructions for responding to one specific alert or failure |
| [`templates/postmortem.md`](templates/postmortem.md) | Blameless post-incident review |
| [`templates/cast-analysis.md`](templates/cast-analysis.md) | In-depth systemic analysis (CAST) for SEV0 or repeat incidents |
| [`templates/status-update.md`](templates/status-update.md) | Ready-to-use wording for internal and customer updates |

## Severity levels

Severity is based on **user impact**, never on how hard the problem is to fix.
When in doubt, choose the more severe level (the lower number); downgrading
later is cheap. Severity does not depend on the service tier: a less critical
service can still cause a SEV0, for example by exposing data.

| Level | Definition | Examples | Response |
| --- | --- | --- | --- |
| **SEV0** | Critical service unavailable or data at risk for many users | Nobody can sign in; data loss or exposure; security breach | Page immediately, 24/7. Incident commander assigned within 5 minutes of declaring. Internal and customer updates every 30 minutes. Executive notified. |
| **SEV1** | Major feature degraded, or a critical service down for a subset of users | Checkout failing for one region; about 1 in 20 checkout attempts failing | Page immediately, 24/7. Incident commander assigned within 15 minutes. Internal updates every 60 minutes; customer updates if customers can see the impact. |
| **SEV2** | Minor degradation with a workaround | Slow reports; one non-critical integration failing | Handled in business hours. Ticket tracked to resolution. |
| **SEV3** | No current user impact, but risk if left alone | Backup job failed once; disk at 80% | Ticket in the owning team's backlog. |

SEV0 and SEV1 always get a postmortem. So does any incident that consumes more
than 20% of an error budget on its own (see the
[error budget policy](../slo/templates/error-budget-policy.md)). SEV2 gets one
if it repeats or reveals a systemic gap.

## Roles

For SEV0 and SEV1, these roles are assigned explicitly and announced in the
incident channel. One person may hold several roles in a small team, but the
incident commander should not also be the person typing the fix.

| Role | Responsibility |
| --- | --- |
| **Incident commander (IC)** | Owns the incident end to end. Sets priorities, assigns tasks, decides when to escalate and when it is resolved. Does not debug. |
| **Operations lead** | Investigates and applies changes. Announces every action before taking it. |
| **Communications lead** | Posts internal and customer updates on schedule using the status update template. |
| **Scribe** | Keeps a timestamped log of observations, decisions and actions. The log becomes the postmortem timeline. This role can be filled, or assisted, by an AI transcription tool that records the incident call and channel and posts regular summaries, so people joining late or following along catch up without interrupting responders. Participants are told the call is recorded and transcribed, the tool follows the same [data handling](#ai-agents-in-incident-response) rules as the AI investigation agent, and the IC or a human scribe checks the summaries for accuracy. |
| **Subject matter experts** | Pulled in by the IC as needed. |
| **AI investigation agent** (optional) | Assists the operations lead with investigation. Never holds any of the roles above. See [AI agents in incident response](#ai-agents-in-incident-response). |

Hand roles over explicitly: the outgoing holder posts the current status, open
actions and time of the next update, and the new holder confirms in the
channel. For incidents longer than a few hours, plan handovers so nobody holds
a role while exhausted.

## Lifecycle

Steps 2 to 6 apply in full to SEV0 and SEV1. SEV2 and SEV3 are tracked in a
ticket; open a channel only if several people need to coordinate.

1. **Detect.** An SLO burn-rate alert (the error budget is being used up too
   fast), a monitor or a user report.
   Prefer alerts based on user impact (see the [SLO module](../slo/)).
2. **Declare.** Anyone may declare an incident. Open a dedicated channel and
   name it after the incident ID: `inc-` followed by the next number in a
   single, ever-increasing sequence (for example `inc-1042`). IDs stay unique
   even with several incidents on the same day; put the short description in
   the channel topic, not the name. Set a severity.
3. **Assemble.** Assign the IC and other roles. Until someone takes over, the
   person who declared the incident is the IC; for SEV0 and SEV1, page a
   dedicated IC as soon as you need to work on the fix yourself. Post the first
   internal update within 15 minutes.
4. **Mitigate first, diagnose later.** Restore service before finding the root
   cause. The fastest mitigations, in order of preference:
   - roll back the most recent change (deploy, configuration, feature flag);
   - shift traffic away from the failing zone, region or cluster;
   - add capacity;
   - turn off the failing feature;
   - restore from backup, only when data is affected.
5. **Resolve.** The IC declares resolution once the SLIs (the measurements
   behind the SLOs, such as the share of requests that succeed), measured over
   a short window such as 5 minutes, are back to normal and have stayed there
   for an agreed period (for example 30 minutes). For incidents not visible in
   SLIs (security, data), the IC declares resolution once impact has ended and
   no further harm is expected. Post the final "Resolved" update.
6. **Learn.** Name a postmortem owner at resolution. Publish the draft and hold
   the review within five business days. Track every action item to completion.

## On-call

- Primary and secondary on-call for every Tier 1 and Tier 2 service (see
  [service tiers](../governance/README.md#1-service-tiers)). Pages are
  acknowledged within 5 minutes.
- A written handoff at each shift change: open incidents, recent changes,
  noisy alerts.
- Follow-the-sun rotations where teams span time zones, to avoid night pages.
- Keep rotations sustainable. Google's SRE guidance is at least 8 people at a
  single site (or 6 per site across two sites) and no more than about 2
  incidents per 12-hour shift.
- Time off after a night spent on an incident.
- New incident commanders shadow experienced ones before leading.


## AI agents in incident response

AI agents are increasingly used as investigation helpers: searching logs,
metrics and traces, correlating recent changes, and suggesting likely causes.
They can save valuable minutes, but only within clear limits.

**The agent's role**

- It is an **assistant to the operations lead**, comparable to a subject
  matter expert. It never acts as incident commander, and accountability for
  every decision stays with humans.
- Its output is a **hypothesis with evidence**: each finding links to the
  query, dashboard, log lines or change it is based on, so a human can verify
  it quickly. Unsupported conclusions are treated as noise.

**Permissions**

- **Read-only by default**: observability data, deployment history,
  configuration, runbooks and past postmortems.
- **Any change requires explicit human approval**, either at the time or in
  advance for low-risk actions marked as pre-approved in the service's runbook
  (for example, rolling back the last deployment of one service). Every change
  is announced in the incident channel before it happens, like any other
  action.
- Treat everything the agent reads (logs, tickets, alert text) as untrusted:
  it can contain instructions planted by an attacker (prompt injection). This
  is one more reason the agent is read-only and changes need human approval.
- Its credentials are dedicated, least-privilege and audited, and can be
  revoked instantly.

**Working in the incident**

- The agent posts in the incident channel (or a linked thread) so its
  findings are visible to everyone and land in the timeline.
- The incident commander can stop or silence it at any time if it becomes a
  distraction.
- Responders do not wait on it: mitigation proceeds in parallel.

**Data handling**

- Only send data to an AI service that the organization has approved for that
  data's sensitivity. Secrets and personal data are masked before they leave
  the system.

**Learning**

- The postmortem notes what the agent contributed, what it got wrong, and
  whether it sped up or slowed down mitigation. Use this to decide where to
  trust it more, and where less.

## Communication rules

- One channel per incident. Side conversations are moved into it.
- Updates follow a fixed format: impact, current status, next step, time of
  the next update. See [`templates/status-update.md`](templates/status-update.md).
- Customer-facing updates state facts and impact, not speculation about
  causes.
- If nothing has changed, post an update saying so. Silence causes more alarm
  than bad news.
- **Security incidents and data exposure** follow the security incident
  process instead: a private channel on a need-to-know basis, the security
  team as IC or co-IC, and legal and privacy involved early, because
  notification deadlines may apply (for example 72 hours under the GDPR).
  Postmortems are shared once security and legal approve.

## Runbooks

Every alert that can page a human must link to a runbook. A good runbook:

- can be followed by an engineer who has never seen the service, at 3 a.m.;
- starts with how to confirm user impact and how to mitigate, before
  diagnosis;
- contains copy-paste commands and links to dashboards, not prose
  descriptions of them;
- is reviewed after each use and at least every six months;
- is tested by someone other than its author.

Practise with game days or tabletop exercises, so the first real use of a
runbook is not the first use.

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
- Review the draft in a meeting with the responders and a facilitator from
  outside the team.
- Share postmortems widely (after security and legal approval where needed).
  Other teams learn from them too.
- Hold a regular (for example weekly) incident review across teams to read
  recent postmortems and chase overdue action items. Near misses are welcome.

## CAST: deeper analysis for major incidents

A blameless postmortem sets the culture and the format. **CAST** (Causal
Analysis based on System Theory, developed by Nancy Leveson at MIT) is a
rigorous method to use inside it when an incident deserves a deeper look.

Instead of a chain of events ending in a "root cause", CAST asks how the
**control structure** failed: which people, processes and automated systems
were responsible for preventing the hazard, what each of them believed about
the system at the time, why that belief was wrong (missing, late or
misleading feedback), and what pressures shaped their decisions (conflicting
goals, drift over time). This leads to
fixes in feedback loops, constraints and responsibilities, rather than
"be more careful".

They go hand in hand:

| | Blameless postmortem | CAST |
| --- | --- | --- |
| Used for | Every SEV0 and SEV1 | SEV0, repeat incidents, or when the postmortem stops at "human error" |
| Focus | What happened, impact, timeline, actions | Why the system's controls allowed it |
| Output | Action items | Changes to the control structure, plus action items |
| Effort | Hours | A few days with a trained facilitator |

Template: [`templates/cast-analysis.md`](templates/cast-analysis.md).

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
| Detected by alerts | Share of incidents detected by monitoring rather than by users |

Report medians per severity and look at trends over quarters, not single
months: with few incidents, monthly numbers are mostly noise. Never set targets
on the number of incidents; it discourages people from declaring them.
