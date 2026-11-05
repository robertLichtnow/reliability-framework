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
[production readiness review](../governance/templates/production-readiness-review.md).
The full standard applies to Tier 1 and Tier 2 services; Tier 3 services need
at least basic monitoring (see [service tiers](../governance/README.md#1-service-tiers)).

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
  use. It becomes critical infrastructure, so run it redundantly (an agent per
  node plus a gateway tier), with memory limits and batching, and monitor the
  data it refuses or drops.
- Logs: OpenTelemetry log support is mature in the Collector and in some
  languages (for example Java and .NET) but still maturing in others (check
  the [status table](https://opentelemetry.io/docs/languages/)). Keep the
  language's normal logging library and connect it through an OpenTelemetry
  log bridge, or write JSON to standard output and let the Collector collect
  it. Either way, include `trace_id` and `span_id`.

Proprietary agents and vendor-specific libraries should be the exception.

### Cost: metrics first, sample logs and traces

Logs and traces are expensive to collect, ship, store and search; at scale
they can rival the cost of the systems they describe. Metrics are cheap
because they summarize many events into a few numbers.

- **Default to metrics.** If a question can be answered with a counter or a
  histogram ("how many", "how fast", "how often did it fail"), use a metric,
  not a log line or a trace.
- **Sample logs and traces wherever possible**, for example a small
  percentage of successful requests.
- **Always keep errors.** Never sample away error logs, or traces of failed or
  unusually slow requests; those are the ones needed during an incident. To
  survive error floods, rate-limit exact repeats and count what was
  suppressed, but keep every distinct error.
- **Derive metrics before sampling.** Counts and latencies computed from
  sampled traces undercount; use metrics instrumentation, or generate metrics
  from spans in the Collector before the sampler.
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
| **D**uration | Latency histogram | Use histograms, not averages. Averages hide the slow requests users notice. Make every SLO latency threshold (for example 300 ms) an exact bucket boundary, or use native (exponential) histograms; a threshold between buckets cannot be measured. |

**For every resource (hosts, containers, databases, queues), the USE method:**

| Signal | Example |
| --- | --- |
| **U**tilization | CPU %, memory %, connection pool in use |
| **S**aturation | Run queue, queue depth, throttling, pending connections |
| **E**rrors | Disk errors, out-of-memory kills, failed health checks |

**Naming and labels**

- With OpenTelemetry, use the semantic-convention name where one exists (for
  example `http.server.request.duration`, in seconds); the Prometheus exporter
  adds unit and `_total` suffixes. For custom metrics follow the
  [Prometheus naming conventions](https://prometheus.io/docs/practices/naming/):
  base units (`_seconds`, `_bytes`), `_total` suffix for counters.
- Every signal (metrics, logs, traces) carries the same identifying
  attributes: `service.name`, `service.version`, `deployment.environment.name`,
  and `cloud.region` or `k8s.cluster.name`. In Prometheus, `service.name`
  becomes the `job` label and the others are not labels by default; promote
  the ones dashboards, SLO queries and canary analysis filter on (the version
  is needed to compare a canary with the current release).
- **Never** use unbounded values as labels (user IDs, request IDs, email
  addresses, raw URL paths; use the route template such as `/orders/{id}`).
  They multiply storage cost and can expose personal data. Give each service a
  budget for active series and alert when it is exceeded.
- Enable **exemplars**, so a spike on a latency or error graph links to an
  example trace.
- Compute percentiles from histograms summed across instances, never by
  averaging each instance's percentiles.
- Retention: at least the longest SLO window (for example 30 days) at full
  resolution, and about 13 months downsampled for capacity planning.

### 2. Logs

Logs record individual events for diagnosis.

- **Structured** (JSON), one event per line, written to standard output.
- Required fields: `timestamp` (UTC, ISO 8601), `level`, `service`,
  `version`, `environment`, `region`, `message`, and `trace_id` and `span_id`
  when available.
- Levels: `ERROR` (needs attention), `WARN` (unexpected but handled), `INFO`
  (significant business events), `DEBUG` (disabled in production by default).
- **No secrets or personal data** in logs: passwords, tokens, card numbers,
  full names, government ID numbers. Mask or omit them at the source.
  Automatic instrumentation can record URLs with query strings, SQL statements
  and headers; review what it captures and scrub in the Collector.
- Sample high-volume `INFO` and `DEBUG` logs; keep every `WARN` and `ERROR`.
  Audit and security logs (who did what, when) are a separate stream and are
  never sampled.
- Retention: at least 30 days searchable; longer or shorter where regulation
  requires it.

### 3. Traces

Distributed traces follow one request across every service it touches.

- Instrument with OpenTelemetry (see [OpenTelemetry by default](#opentelemetry-by-default)),
  using automatic instrumentation for common frameworks and manual spans for
  important business operations.
- Propagate context with the [W3C Trace Context](https://www.w3.org/TR/trace-context/)
  headers (or message attributes for queues) across every network call.
- Sample: keep every trace with an error or high latency, and only a small
  percentage of normal traffic. Only tail-based sampling can guarantee this,
  because errors are known at the end: the Collector buffers each trace's
  spans for a fixed wait (for example 30 seconds), then decides. All spans of
  a trace must reach the same Collector instance, so route them by trace ID
  through a load-balancing Collector tier. Long asynchronous flows (a queue
  consumer running minutes later) should start their own trace, linked to the
  producer's span.

### 4. Dashboards

Each service has one **overview dashboard**, with the same layout everywhere:

1. SLO status and remaining error budget
2. Request rate, error rate, latency percentiles (p50, p95, p99: the time
   within which half, 95% and 99% of requests finish), with successful and
   failed requests shown separately
3. Saturation of the main resources
4. Dependencies: their error rate and latency as seen by this service
5. Recent deployments and configuration changes as annotations

### 5. Alerts

- Page a human only for **user-facing symptoms**, preferably SLO burn rate
  (see the [SLO module](../slo/)).
- Causes (high CPU, a disk filling up with days of headroom) become tickets,
  not pages. Exception: page on a cause that will hit users before an SLO
  alert could fire, such as a disk predicted to fill within hours or a
  certificate about to expire.
- Every paging alert links to a [runbook](../incident-response/templates/runbook.md)
  and a dashboard.
- Review alert volume monthly. More than two incidents per 12-hour on-call shift is a
  signal to fix the system or the alerts.

### 6. Change tracking

Most incidents follow a change. Record every deployment, configuration change,
feature flag change and infrastructure change as an event that appears on
dashboards, with who made it and a link to the change.

## Checklist

| # | Requirement | Done |
| --- | --- | --- |
| 1 | OpenTelemetry for traces and metrics; logs bridged or collected into OpenTelemetry; W3C context propagation | ☐ |
| 2 | Metrics used by default; logs and traces sampled, with errors always kept | ☐ |
| 3 | RED metrics for every endpoint, latency as a histogram with SLO thresholds as bucket boundaries | ☐ |
| 4 | USE metrics for every resource the service owns | ☐ |
| 5 | Standard identifying attributes on every signal; no unbounded label values | ☐ |
| 6 | Structured JSON logs with required fields | ☐ |
| 7 | No secrets or personal data in logs, metrics or traces | ☐ |
| 8 | Standard overview dashboard | ☐ |
| 9 | SLOs defined and burn-rate alerts in place | ☐ |
| 10 | Every paging alert links to a runbook and a dashboard | ☐ |
| 11 | Deployments and config changes shown on dashboards | ☐ |
