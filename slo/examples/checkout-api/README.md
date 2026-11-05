[Reliability Framework](../../../README.md) › [Service Level Objectives](../../) › **Worked example**

# Worked example: checkout service

A complete, filled-in set of reliability targets for a fictional online
store's checkout service. Use it to see what the finished result looks like
before filling in the [blank templates](../../templates/).

| File | What it is | Who reads it |
| --- | --- | --- |
| [`slo-document.md`](slo-document.md) | **Start here.** The human-readable SLO document: users, targets, reasons, alerts | Everyone |
| [`slo.yaml`](slo.yaml) | The same targets in a machine-readable form | Engineers, the [SLO tool](../../../tools/) |
| [`prometheus-rules.yaml`](prometheus-rules.yaml) | Monitoring alerts generated from `slo.yaml` by the tool. Do not edit by hand | Monitoring system |
| [`alerts-test.yaml`](alerts-test.yaml) | Automated tests proving the alerts fire during an outage and stay quiet when healthy | Engineers, CI |

All numbers are illustrative.
