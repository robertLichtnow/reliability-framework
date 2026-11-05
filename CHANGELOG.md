# Changelog

## Unreleased

**Easier to read and navigate.**

- New front page: what site reliability engineering is, where to start by
  role, the eight modules as a numbered path with reading times, and every
  template in one table.
- New [glossary](docs/glossary.md) of plain-language definitions.
- Every module has a breadcrumb, audience and reading time, a highlighted
  plain-language summary, an "On this page" contents list, and previous/next
  links.
- Short guide pages for the templates folders, the worked example and the
  SLO tool.

**Expert review pass.** Five independent SRE reviews of every module; findings
applied below.

- **SLOs and tool**
  - Generated rules now alert when only errors are being recorded (missing
    "good" series count as 100% errors) and return no data instead of NaN when
    there is no traffic.
  - Windows limited to 7 to 90 days; burn rates scaled for other windows and
    never below 1; objectives too low for an alert to ever fire are rejected;
    validator hardened against malformed input.
  - Alerts carry `runbook_url` and `dashboard_url`; new full-window and
    `slo:error_budget_remaining:ratio` recording rules.
  - Promtool unit tests prove the example alerts fire in an outage and stay
    quiet when healthy; CI checks rules from every `slo.yaml` with Prometheus 3.
  - Guide covers missing data, low traffic, retention and alert grouping;
    example payment SLI counts confirmations that never arrive.
  - Error budget policy: dependency failures still count in the SLI.
- **Incident response**
  - Severity levels renumbered to SEV0 (most critical) through SEV3 (each
    level moves up one: old SEV1 is now SEV0, old SEV4 is now SEV3).
  - Sequential incident IDs (`inc-1042`); on-call section; role handoffs;
    security and data incidents handled privately with legal; clearer update
    cadence, resolution and postmortem triggers.
  - AI investigation agent guidance (role, permissions, prompt injection, data
    handling) and AI-assisted scribe with consent rules.
  - CAST analysis section and template alongside blameless postmortems.
- **Observability**: OpenTelemetry by default (with honest notes on log
  maturity and Collector operations), metrics first with sampled logs and
  traces that always keep errors, shared identifying attributes, cardinality
  budgets, exemplars, tail-sampling requirements.
- **Kubernetes**
  - Checklist adds node sizing, service mesh rate limiting, capacity type per
    workload, overprovisioning with pause pods, autoscaling (KEDA by default).
  - Example manifests: zone spread that survives a zone outage and rollouts,
    no `replicas` under an autoscaler, safer readiness probe, writable `/tmp`,
    PDB eviction policy; buffer in its own namespace.
  - Karpenter node pool example; NodeLocal DNSCache; safer upgrade order;
    blue/green covers cluster operators, background jobs, capacity and DNS.
  - Reference architecture is now an SVG image.
- **Database**: corrected expand-and-contract steps; failover, pooling,
  timeouts, backups, online migrations, major-version upgrades and extra
  signals.
- **Event-driven**: fairness between customers; idempotency, poison messages,
  retry budgets, circuit breakers that pause consumption, schema
  compatibility in both directions, outbox and retention monitoring.
- **New module: Safe delivery**, built around "unobserved is unproven":
  production-grade staging, canary deployments judged on their own metrics,
  gradual traffic shifting and rollback.
- **Governance**: tier requirements aligned with other modules, tier
  inheritance, emergency changes, recovery readiness in reports.

## 0.2.0 (2026-11-05)

- New modules: incident response, observability standards, high-availability
  Kubernetes, database reliability, event-driven systems, governance.
- Templates: runbook, postmortem, status updates, production readiness
  review, reliability report.
- Annotated highly available Kubernetes Deployment example, validated in CI.

## 0.1.0 (2026-11-05)

- First module: Service Level Objectives.
  - Step-by-step guide (`slo/README.md`).
  - Templates: SLO document, machine-readable `slo.yaml`, error budget policy.
  - Complete example for a fictional checkout API.
  - `tools/slo_tool.py`: validates SLO files, prints error budgets, and
    generates Prometheus recording and multi-window, multi-burn-rate alerting
    rules.
