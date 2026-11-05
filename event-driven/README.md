[Reliability Framework](../README.md) › Module 7 of 8

# Event-driven systems

Guidelines for building systems that communicate through queues and events
without losing messages, acting on them twice, letting one failure spread
to everything else, or letting one customer crowd out all the others.

*For engineers building services that exchange messages · About 10 minutes to read · New to a term? See the [glossary](../docs/glossary.md).*

> [!NOTE]
> **In plain language.** Modern systems are made of many services that pass messages to each other:
> "order placed", "payment received", "appointment booked". Sending these
> messages through a queue lets each service work at its own pace and keeps a
> problem in one place from stopping everything. But queues introduce their own
> risks: messages can be lost, delivered twice or stuck. This module describes
> the patterns that make event-driven systems dependable.

## On this page

- [When to use events](#when-to-use-events)
- [Core guidelines](#core-guidelines)
  - [1. Assume at-least-once delivery; make consumers idempotent](#1-assume-at-least-once-delivery-make-consumers-idempotent)
  - [2. Never lose a message between the database and the queue](#2-never-lose-a-message-between-the-database-and-the-queue)
  - [3. Retry with backoff, then park the message](#3-retry-with-backoff-then-park-the-message)
  - [4. Protect against overload](#4-protect-against-overload)
  - [5. Design events as contracts](#5-design-events-as-contracts)
  - [6. Ordering](#6-ordering)
  - [7. Fairness between customers (tenants)](#7-fairness-between-customers-tenants)
  - [8. Observability](#8-observability)
- [Checklist](#checklist)

## When to use events

| Use events / queues when | Use a direct request when |
| --- | --- |
| The sender does not need an immediate answer | The user is waiting for the result |
| Work can be retried later (emails, webhooks, reports) | The operation must succeed or fail as one unit right now |
| Traffic is bursty and needs smoothing | Ordering and consistency are simpler with one call |
| Several consumers react to the same fact | Only one consumer exists and latency matters |

## Core guidelines

### 1. Assume at-least-once delivery; make consumers idempotent

Almost every queue delivers some messages more than once. A consumer is
**idempotent** when processing the same message twice has the same effect as
processing it once.

- Give every message a unique, stable `id` set by the producer.
- Record processed ids (or use a natural key with a unique constraint) and
  skip duplicates. Write the record in the same database transaction as the
  change the message causes, so a crash cannot leave one without the other,
  and keep ids at least as long as a message can be redelivered or replayed,
  including dead-letter replays days later.
- For external side effects (charging a card, sending a webhook), pass an
  idempotency key to the downstream system.
- Treat "exactly-once" features (broker transactions, deduplication windows)
  as covering only part of the path; side effects outside it, such as a
  database write, a payment or an email, still need idempotency.

### 2. Never lose a message between the database and the queue

Writing to a database and publishing to a queue are two separate operations;
if the process crashes between them, the system becomes inconsistent.

Use the **transactional outbox**: write the event to an `outbox` table in the
same database transaction as the business change, and have a separate relay
publish outbox rows to the queue and mark them sent. The relay can poll the
table, or use change data capture (reading the database's own change log, for
example with Debezium).

### 3. Retry with backoff, then park the message

- Retry transient failures with **exponential backoff and jitter** (random
  spread), with a cap on attempts.
- Retry in one layer only, or cap retries with a budget: three layers that
  each try three times turn one failure into 27 calls on a dependency that is
  already struggling.
- After the last attempt, move the message to a **dead-letter queue (DLQ)**.
  Never drop it silently and never retry forever.
- Count delivery attempts on the broker side (for example a maximum receive
  count) as well as in code, so a message that crashes or hangs the consumer
  (a *poison message*) still reaches the DLQ instead of crash-looping every
  consumer. In partitioned logs a stuck message blocks its whole partition;
  move it to a retry or dead-letter topic rather than retrying in place.
- Open a ticket when the DLQ is not empty; page only if a critical flow is
  affected and has no freshness SLO to catch it. Provide a documented, tested
  way to inspect and replay DLQ messages.
- Distinguish errors that will never succeed (invalid data) from transient
  ones (timeouts); send the former to the DLQ immediately.

### 4. Protect against overload

- **Bound every queue and every consumer's concurrency.** Unbounded work is
  how one slow dependency takes down the whole system.
- Use **backpressure**: consumers pull only as much work as they can handle,
  and when a queue reaches its bound, producers are slowed or told to retry
  later (for example HTTP 429 or 503), so overload is pushed back to its
  source instead of piling up or being lost.
- Put **timeouts** on every network call and **circuit breakers** around
  dependencies, so a failing dependency is detected quickly instead of tying
  up every worker. In a queue consumer, an open circuit should **pause
  consumption** (stop pulling and leave messages in the queue) rather than
  fail each message; otherwise a downstream outage burns through every
  message's retries and floods the DLQ with valid work.
- Keep processing time well inside the broker's lease (visibility timeout,
  maximum poll interval), or extend it while working; otherwise the message
  goes to a second consumer while the first is still processing it.
- Autoscale consumers on queue depth or message age (for example with
  [KEDA](../kubernetes/README.md#choosing-an-autoscaler) on Kubernetes), with a
  maximum that the downstream systems can handle. In partitioned logs,
  consumers beyond the partition count sit idle, so the partition count is the
  real scaling ceiling.

### 5. Design events as contracts

- Events describe facts in the past tense (`OrderPlaced`). Commands sent to a
  work queue (`SendReceipt`) are fine too; keep them distinct: an event can
  have many consumers, a command has one owner.
- Use a schema (JSON Schema, Avro or Protobuf) with a registry or versioned
  files. Changes must be compatible in both directions: consumers still on the
  old schema must read new events, and upgraded consumers must read old events
  still in the queue or replayed. Add optional fields with defaults; never
  remove, rename or repurpose fields or change their type. A breaking change
  is a new event type or version, published alongside the old one until every
  consumer has moved. Check compatibility automatically in CI or in the
  registry.
- Include standard metadata. The [CloudEvents](https://cloudevents.io/)
  specification defines a common format: `id`, `type`, `source`, `time`,
  `dataschema`, and trace context (`traceparent`). Add a tenant id where
  fairness (section 7) depends on it.

### 6. Ordering

Do not rely on global ordering. Where order matters (events for one account),
use a partition or message group key (a label, such as the account number,
that keeps related messages in one line) so they are processed in sequence.
Make consumers tolerate out-of-order or stale events by comparing version or
sequence numbers set by the source of truth; timestamps from different
machines can disagree. Moving a message to a retry queue or DLQ breaks per-key
order; where order matters, hold later messages for that key until the failed
one is resolved.

### 7. Fairness between customers (tenants)

In a shared queue, one customer who suddenly sends a huge burst of work can
fill the queue, and everyone else's messages wait behind it. Each message is
still processed eventually, but for most customers the service looks down.
Design so that **no single customer can take over shared capacity**:

- **Per-tenant limits at the entrance.** Rate-limit or cap how much work each
  customer can enqueue per period; reject or defer the excess with a clear
  signal rather than silently queueing it.
- **Fair scheduling inside.** Instead of one first-in, first-out queue, give
  each tenant (or group of tenants) its own logical queue or message group and
  have consumers take work from them in turn (round-robin or weighted fair
  queuing). Some managed queues do this when each message carries a tenant or
  group key (for example Amazon SQS fair queues). A partition key in a log
  such as Kafka gives ordering, not fairness: many tenants share each
  partition, so a heavy tenant still delays everyone on its partition; there,
  the consumer must schedule fairly itself, or heavy tenants need their own
  topics.
- **Per-tenant concurrency caps.** Limit how many workers can process one
  tenant's messages at the same time, so a heavy tenant uses its share and no
  more.
- **Isolate the heaviest workloads.** Route very large or known-noisy tenants,
  or bulk operations such as imports and backfills, to separate queues and
  workers (the *bulkhead* pattern). Two stronger forms exist: a *cell-based
  architecture* gives each group of tenants its own complete, independent copy
  of the system; *shuffle sharding* assigns each tenant a small random
  combination of workers or queues out of a larger pool, so a noisy tenant
  affects only a small fraction of the others.
- **Measure per tenant, within a cardinality budget.** Track queue age and
  processing latency per tenant, not just overall; an average can look healthy
  while one group of customers is stuck. Use the tenant id as a metric label
  only when the number of tenants is small and fixed; otherwise label by
  tenant tier or shard, export the busiest tenants by name with the rest as
  `other`, and keep full per-tenant detail in logs and traces (see
  [labels](../observability/README.md#1-metrics)).

### 8. Observability

In addition to the [observability standard](../observability/), monitor:

| Signal | Why |
| --- | --- |
| **Age of oldest message** | The best single indicator of user impact; depth alone can mislead |
| Queue depth and growth rate | Consumers falling behind |
| Processing rate and error rate per consumer | Failing or slow consumers |
| Retry count and DLQ size | Systematic failures |
| End-to-end latency (event time to processing complete) | Basis for a freshness SLO |
| Queue age and throughput **per tenant** (or per tier, within the label budget) | Detects one customer starving the others |
| Outbox backlog (age of the oldest unpublished row) | A stalled relay stops all events while the queue itself looks empty and healthy |
| Oldest message age vs. the queue's retention limit | Messages older than the retention period are deleted without warning |

For Kafka-style logs the equivalents are consumer-group lag in messages
(depth) and lag in time (age); time lag usually needs an exporter.

Define a **freshness SLO** for important flows, for example "99.9% of payment
confirmations delivered to the order system within 60 seconds" (see the
[SLO example](../slo/examples/checkout-api/slo-document.md)). Measure it from
the event's creation time to where processing completes, and pair it with an
alert on the age of the oldest message: an SLI computed from completed
messages cannot see messages that are stuck.

## Checklist

| # | Requirement | Done |
| --- | --- | --- |
| 1 | Every message has a unique id; consumers are idempotent | ☐ |
| 2 | Transactional outbox (relayed by polling or change data capture) for database-to-queue publishing | ☐ |
| 3 | Exponential backoff with jitter, a retry cap, and retries in one layer only | ☐ |
| 4 | Dead-letter queue with poison-message handling, alerting and a tested replay procedure | ☐ |
| 5 | Bounded queues and concurrency; backpressure to producers; timeouts and circuit breakers that pause consumption | ☐ |
| 6 | Versioned event schemas, compatible in both directions | ☐ |
| 7 | Ordering handled per key where required | ☐ |
| 8 | Per-tenant limits, fair scheduling, concurrency caps and isolation of heavy workloads | ☐ |
| 9 | Message age, DLQ size, outbox backlog, end-to-end latency and per-tenant (or per-tier) age monitored | ☐ |
| 10 | Freshness SLO for critical flows | ☐ |
| 11 | Consumer autoscaling with a maximum the downstream systems can handle | ☐ |

---

| Previous | Overview | Next |
| :--- | :---: | ---: |
| [← 6. Database reliability](../database/) | [All modules](../README.md#the-eight-modules) | [8. Governance →](../governance/) |
