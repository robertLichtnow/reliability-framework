# Changelog

## Unreleased

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
