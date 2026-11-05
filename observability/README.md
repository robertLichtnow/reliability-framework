# Observability Standards

What every production service should measure, log and trace, so that problems
are detected quickly and diagnosed without guesswork.

## Summary for non-engineers

A service that cannot be observed cannot be kept reliable. When something
goes wrong, engineers need to answer three questions quickly: *Are users
affected? Where is the problem? Why did it happen?* This module sets a
minimum standard so every service answers those questions the same way,
using open standards that work with any vendor.

## Principle: unobserved is unproven

If a component is not being used, or cannot be observed, there is no evidence
that it works. Instrument everything, and make sure important paths carry real
or synthetic traffic so their telemetry means something (see
[Safe delivery](../safe-delivery/README.md#core-principle-unobserved-is-unproven)).

## The minimum standard

Every service in production must meet the requirements below. Use the
[checklist](#checklist) during design reviews and the
[production readiness review](../governance/).

### OpenTelemetry by default

Use [OpenTelemetry](https://opentelemetry.io/) for traces, metrics and logs
unless there is a very good, documented reason not to.

- It is the most widely accepted observability standard, maintained under the
  Cloud Native Computing Foundation.
- Virtually every monitoring tool and vendor accepts it, and every major
  language and framework has OpenTelemetry libraries.
- Instrumenting once with OpenTelemetry means the organization can change
  monitoring vendors, or use several, without touching application code.
- Run the OpenTelemetry Collector as the single pipeline for telemetry:
  it receives, filters, samples and routes data to whichever backends are in
  use.

Proprietary agents and vendor-specific libraries should be the exception.

### Cost: metrics first, sample logs and traces

Logs and traces are expensive to collect, ship, store and search; at scale
they often cost more than the systems they describe. Metrics are cheap
because they summarize many events into a few numbers.

- **Default to metrics.** If a question can be answered with a counter or a
  histogram ("how many", "how fast", "how often did it fail"), use a metric,
  not a log line or a trace.
- **Sample logs and traces wherever possible**, for example a small
  percentage of successful requests.
- **Always keep errors.** Never sample away error logs, or traces of failed or
  unusually slow requests; those are the ones needed during an incident.
- Review observability spend regularly, and drop or downsample signals nobody
  uses.

### 1. Metrics

Metrics are numbers measured over time. They power dashboards, SLOs and
alerts.

**For every request-driven service (APIs, web apps), the RED method:**

| Signal | Metric | Notes |
| --- | --- | --- |
| **R**ate | Requests per second | Labeled by route and response class |
| **E**rrors | Failed requests per second | Server errors (5xx) separately from client errors (4xx) |
| **D**uration | Latency histogram | Use histograms, not averages. Averages hide the slow requests users notice. |

**For every resource (hosts, containers, databases, queues), the USE method:**

| Signal | Example |
| --- | --- |
| **U**tilization | CPU %, memory %, connection pool in use |
| **S**aturation | Run queue, queue depth, throttling, pending connections |
| **E**rrors | Disk errors, out-of-memory kills, failed health checks |

**Naming and labels**

- Follow the [Prometheus naming conventions](https://prometheus.io/docs/practices/naming/):
  base units (`_seconds`, `_bytes`), `_total` suffix for counters.
- Every metric carries `service`, `environment` and `region` (or `cluster`)
  labels.
- **Never** use unbounded values as labels (user IDs, request IDs, email
  addresses, full URLs). They multiply storage cost and can expose personal
  data.

### 2. Logs

Logs record individual events for diagnosis.

- **Structured** (JSON), one event per line, written to standard output.
- Required fields: `timestamp` (UTC, ISO 8601), `level`, `service`,
  `environment`, `message`, `trace_id`, `span_id` when available.
- Levels: `ERROR` (needs attention), `WARN` (unexpected but handled), `INFO`
  (significant business events), `DEBUG` (disabled in production by default).
- **No secrets or personal data** in logs: passwords, tokens, card numbers,
  full names, government ID numbers. Mask or omit them at the source.
- Sample high-volume `INFO` and `DEBUG` logs; keep every `WARN` and `ERROR`.
- Retention: at least 30 days searchable; longer where regulation requires it.

### 3. Traces

Distributed traces follow one request across every service it touches.

- Instrument with OpenTelemetry (see [OpenTelemetry by default](#opentelemetry-by-default)),
  using automatic instrumentation for common frameworks and manual spans for
  important business operations.
- Propagate context with the [W3C Trace Context](https://www.w3.org/TR/trace-context/)
  headers across every network call, including message queues.
- Sample: keep every trace with an error or high latency, and only a small
  percentage of normal traffic (tail-based sampling in the OpenTelemetry
  Collector makes this decision after the request completes).

### 4. Dashboards

Each service has one **overview dashboard**, with the same layout everywhere:

1. SLO status and remaining error budget
2. Request rate, error rate, latency percentiles (p50, p95, p99)
3. Saturation of the main resources
4. Dependencies: their error rate and latency as seen by this service
5. Recent deployments and configuration changes as annotations

### 5. Alerts

- Page a human only for **user-facing symptoms**, preferably SLO burn rate
  (see the [SLO module](../slo/)).
- Causes (high CPU, a full disk that is not yet affecting users) become
  tickets, not pages.
- Every paging alert links to a [runbook](../incident-response/templates/runbook.md)
  and a dashboard.
- Review alert volume monthly. More than two pages per on-call shift is a
  signal to fix the system or the alerts.

### 6. Change tracking

Most incidents follow a change. Record every deployment, configuration change,
feature flag change and infrastructure change as an event that appears on
dashboards, with who made it and a link to the change.

## Checklist

| # | Requirement | Done |
| --- | --- | --- |
| 1 | RED metrics for every endpoint, latency as a histogram | ☐ |
| 2 | USE metrics for every resource the service owns | ☐ |
| 3 | Standard labels; no unbounded label values | ☐ |
| 4 | Structured JSON logs with required fields | ☐ |
| 5 | No secrets or personal data in logs, metrics or traces | ☐ |
| 6 | OpenTelemetry for traces, metrics and logs, with W3C context propagation | ☐ |
| 7 | Standard overview dashboard | ☐ |
| 8 | SLOs defined and burn-rate alerts in place | ☐ |
| 9 | Every paging alert links to a runbook | ☐ |
| 10 | Deployments and config changes shown on dashboards | ☐ |
| 11 | Metrics used by default; logs and traces sampled, with errors always kept | ☐ |
