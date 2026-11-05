# Reliable Event-Driven Systems

Guidelines for building systems that communicate through queues and events
without losing messages, processing them twice, letting one failure spread
to everything else, or letting one customer crowd out all the others.

## Summary for non-engineers

Modern systems are made of many services that pass messages to each other:
"order placed", "payment received", "appointment booked". Sending these
messages through a queue lets each service work at its own pace and keeps a
problem in one place from stopping everything. But queues introduce their own
risks: messages can be lost, delivered twice or stuck. This module describes
the patterns that make event-driven systems dependable.

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
  skip duplicates.
- For external side effects (charging a card, sending a webhook), pass an
  idempotency key to the downstream system.

### 2. Never lose a message between the database and the queue

Writing to a database and publishing to a queue are two separate operations;
if the process crashes between them, the system becomes inconsistent.

Use the **transactional outbox**: write the event to an `outbox` table in the
same database transaction as the business change, and have a separate relay
publish outbox rows to the queue and mark them sent. Alternatively, use
change data capture (for example Debezium) on the outbox table.

### 3. Retry with backoff, then park the message

- Retry transient failures with **exponential backoff and jitter** (random
  spread), with a cap on attempts.
- After the last attempt, move the message to a **dead-letter queue (DLQ)**.
  Never drop it silently and never retry forever.
- Alert when the DLQ is not empty. Provide a documented, tested way to
  inspect and replay DLQ messages.
- Distinguish errors that will never succeed (invalid data) from transient
  ones (timeouts); send the former to the DLQ immediately.

### 4. Protect against overload

- **Bound every queue and every consumer's concurrency.** Unbounded work is
  how one slow dependency takes down the whole system.
- Use **backpressure**: consumers pull at the rate they can handle.
- Put **timeouts** on every network call and **circuit breakers** around
  dependencies, so a failing dependency is skipped quickly instead of tying up
  every worker.
- Autoscale consumers on queue depth or message age, with a maximum that the
  downstream systems can handle.

### 5. Design events as contracts

- Events describe facts in the past tense (`OrderPlaced`), not commands.
- Use a schema (JSON Schema, Avro or Protobuf) with a registry or versioned
  files. Changes must be backward compatible: add optional fields, never
  remove or repurpose existing ones.
- Include standard metadata: `id`, `type`, `source`, `time`, `schema
  version`, and trace context. The [CloudEvents](https://cloudevents.io/)
  specification defines a common format.

### 6. Ordering

Do not rely on global ordering. Where order matters (events for one account),
use a partition or message group key so related events are processed in
sequence, and make consumers tolerate out-of-order or stale events by
comparing versions or timestamps.

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
  queuing). Many brokers support this through message group or partition keys.
- **Per-tenant concurrency caps.** Limit how many workers can process one
  tenant's messages at the same time, so a heavy tenant uses its share and no
  more.
- **Isolate the heaviest workloads.** Route very large or known-noisy tenants,
  or bulk operations such as imports and backfills, to separate queues and
  workers (sometimes called shuffle sharding or cell isolation when taken
  further).
- **Measure per tenant.** Track queue age and processing latency per tenant,
  not just overall; an average can look healthy while one group of customers
  is stuck.

### 8. Observability

In addition to the [observability standard](../observability/), monitor:

| Signal | Why |
| --- | --- |
| **Age of oldest message** | The best single indicator of user impact; depth alone can mislead |
| Queue depth and growth rate | Consumers falling behind |
| Processing rate and error rate per consumer | Failing or slow consumers |
| Retry count and DLQ size | Systematic failures |
| End-to-end latency (event time to processing complete) | Basis for a freshness SLO |
| Queue age and throughput **per tenant** | Detects one customer starving the others |

Define a **freshness SLO** for important flows, for example "99.9% of payment
confirmations processed within 60 seconds" (see the
[SLO example](../slo/examples/checkout-api/)).

## Checklist

| # | Requirement | Done |
| --- | --- | --- |
| 1 | Every message has a unique id; consumers are idempotent | ☐ |
| 2 | Transactional outbox (or CDC) for database-to-queue publishing | ☐ |
| 3 | Exponential backoff with jitter and a retry cap | ☐ |
| 4 | Dead-letter queue with alerting and a tested replay procedure | ☐ |
| 5 | Bounded queues and concurrency; timeouts and circuit breakers | ☐ |
| 6 | Versioned, backward-compatible event schemas | ☐ |
| 7 | Ordering handled per key where required | ☐ |
| 8 | Per-tenant limits, fair scheduling and concurrency caps so no customer can monopolize a queue | ☐ |
| 9 | Message age, DLQ size and end-to-end latency monitored | ☐ |
| 10 | Freshness SLO for critical flows | ☐ |
