# Changelog

## Unreleased

- Event-driven: fairness between customers (per-tenant limits, fair
  scheduling, concurrency caps, isolation, per-tenant metrics).
- Incident response: CAST (Causal Analysis based on System Theory) section
  and template, alongside the blameless postmortem.
- Incident response: guidelines for AI investigation agents (role,
  permissions, data handling, learning).
- Incident IDs use a sequential number (`inc-1042`) instead of date and
  description.
- Incident response: the scribe role can be filled or assisted by an AI
  transcription and summary tool.
- Incident severity levels renumbered to SEV0 (most critical) through SEV3.
- Observability: cost guidance (metrics first; sample logs and traces, always
  keep errors).
- New module: Safe delivery (staging as a production-grade gate, canary
  deployments, gradual traffic shifting, rollback) built around the
  principle "unobserved is unproven".
- Kubernetes checklist: node sizing and blast radius, service mesh rate
  limiting, capacity type per workload (no spot for user-facing services),
  overprovisioning with pause pods, with an example manifest.
- NodeLocal DNSCache guideline; blue/green migration extended to cluster
  operators and add-ons (autoscaler, CNI, service mesh, ingress).

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
