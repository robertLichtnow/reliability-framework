[Reliability Framework](../README.md) › **Tools**

# SLO tool

`slo_tool.py` turns an [SLO file](../slo/templates/slo.yaml) into something a
monitoring system can use. It does three things:

| Command | What it does |
| --- | --- |
| `check` | Checks the SLO file for mistakes, such as a target of 100% or a missing field |
| `budget` | Shows each target's error budget, and the alert thresholds |
| `rules` | Generates [Prometheus](https://prometheus.io/) recording and alerting rules |

## Try it

You need Python 3 and one library:

```sh
pip install pyyaml
python tools/slo_tool.py check  slo/examples/checkout-api/slo.yaml
python tools/slo_tool.py budget slo/examples/checkout-api/slo.yaml
python tools/slo_tool.py rules  slo/examples/checkout-api/slo.yaml > rules.yaml
```

Example output of `budget`:

```
Service: checkout-api   Window: 30 days

SLO                     Objective    Budget  Full-outage equiv.
availability               99.95%   0.0500%             21m 36s
latency                     99.0%   1.0000%              7h 12m
payment-confirmation        99.9%   0.1000%             43m 12s
```

The alerts follow the multi-window, multi-burn-rate method from Google's
*The Site Reliability Workbook*; the [SLO guide](../slo/README.md#step-5-alert-on-burn-rate-not-on-every-error)
explains it in plain terms.

## Tests

```sh
python -m unittest discover -s tools -v
```

The same tests, plus Prometheus's own rule checker, run automatically on every
change ([CI workflow](../.github/workflows/ci.yml)).
