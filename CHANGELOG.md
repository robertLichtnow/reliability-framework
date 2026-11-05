# Changelog

## 0.1.0 (2026-11-05)

- First module: Service Level Objectives.
  - Step-by-step guide (`slo/README.md`).
  - Templates: SLO document, machine-readable `slo.yaml`, error budget policy.
  - Complete example for a fictional checkout API.
  - `tools/slo_tool.py`: validates SLO files, prints error budgets, and
    generates Prometheus recording and multi-window, multi-burn-rate alerting
    rules.
