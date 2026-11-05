# Reliability Framework

An open, practical toolkit that helps engineering teams keep online services
dependable: defining how reliable a service must be, measuring it, and acting
before users are affected.

**Author:** Matheus Lichtnow, Site Reliability Engineer
**Status:** Version 0.2 (November 2026).
**License:** MIT. Free for anyone to use, copy and adapt.

---

## In plain language

Hospitals, banks, government agencies and businesses depend on software that
runs in the cloud. When that software goes down, people cannot log in, pay,
file paperwork or reach their records.

Most outages are not caused by a lack of talent. They happen because teams never
agreed on **how reliable a service needs to be**, never **measured** it in a
consistent way, or had **no plan** for what to do when reliability started to
slip.

This repository provides ready-to-use documents and tools that close those
gaps. A team can copy them, fill in the blanks for their own service, and get
a working reliability practice in days instead of months.

### What is a Service Level Objective (SLO)?

An SLO is a written, measurable promise about a service. For example:

> "99.9% of login requests in any 30-day period will succeed in under 300
> milliseconds."

That one sentence answers three questions everyone in an organization cares
about:

1. **What matters to users?** (logins that succeed, and are fast)
2. **How good is good enough?** (99.9%, which allows about 43 minutes of
   failure per month)
3. **How do we know?** (it is measured automatically, all the time)

The small amount of allowed failure is called the **error budget**. While the
budget lasts, teams can ship new features quickly. When it runs out, the team
pauses risky changes and fixes reliability first. This turns "is the system
reliable enough?" from an argument into a number.

---

## What is in this repository

The framework has six modules. Each one opens with a plain-language summary,
then gives guidelines, checklists and ready-to-use templates.

| Module | What it helps with | Key materials |
| --- | --- | --- |
| [Service Level Objectives](slo/) | Deciding how reliable a service must be, and measuring it | Guide, SLO and error budget policy templates, worked example, alert generator tool |
| [Incident response](incident-response/) | Handling outages quickly and learning from them | Severity levels, roles, runbook, postmortem and status update templates |
| [Observability](observability/) | Seeing problems early and diagnosing them fast | Minimum standard for metrics, logs, traces, dashboards and alerts |
| [High-availability Kubernetes](kubernetes/) | Running cloud services that survive failures, and upgrading them safely | Reference architecture, configuration checklist, annotated example, upgrade and migration method |
| [Database reliability](database/) | Protecting data and keeping databases available | Backup and restore standards, safe schema changes, capacity planning |
| [Event-driven systems](event-driven/) | Reliable messaging between services | Idempotency, outbox, retries, dead-letter queues, overload protection |
| [Governance](governance/) | Making reliability routine across an organization | Service tiers, production readiness review, reliability report, adoption path |

## How a team uses it

1. Copy [`slo/templates/slo-document.md`](slo/templates/slo-document.md) and
   fill in the service, its users, and what "working" means to them.
2. Copy [`slo/templates/slo.yaml`](slo/templates/slo.yaml) and write the same
   objectives in a machine-readable form.
3. Run the tool to check the file and generate alerting rules:

   ```sh
   pip install pyyaml
   python tools/slo_tool.py check  slo/examples/checkout-api/slo.yaml
   python tools/slo_tool.py budget slo/examples/checkout-api/slo.yaml
   python tools/slo_tool.py rules  slo/examples/checkout-api/slo.yaml > rules.yaml
   ```

4. Agree on the [error budget policy](slo/templates/error-budget-policy.md)
   with product and leadership, so everyone knows what happens when the budget
   runs out.

## How the modules fit together

```
            Governance: tiers, readiness reviews, reporting
   ┌────────────────────────────┴────────────────────────────┐
   SLOs  ──►  Observability  ──►  Alerts  ──►  Incident response
   (targets)  (measurement)       (burn rate)  (runbooks, postmortems)
   └────────────────────────────┬────────────────────────────┘
        Platform practices: Kubernetes · Databases · Event-driven
```

SLOs define what "reliable" means. Observability measures it. Alerts fire when
the error budget burns too fast. Incident response restores service and feeds
lessons back. The platform modules prevent the most common failures in the
first place, and governance makes sure every important service follows the
same standard.

## Design principles

- **Plain language first.** Every document opens with a summary a
  non-engineer can follow.
- **Vendor neutral.** Works with any cloud provider and any monitoring tool.
  The generated alerts use Prometheus, the most widely adopted open-source
  monitoring standard.
- **Built on established practice.** Follows the methods published in
  Google's *Site Reliability Engineering* and *The Site Reliability Workbook*,
  including multi-window, multi-burn-rate alerting.
- **Copy, fill in, done.** Templates are short and every field explains itself.

## Contributing

Issues and pull requests are welcome. See [CHANGELOG.md](CHANGELOG.md) for
version history.
