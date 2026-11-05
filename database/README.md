[Reliability Framework](../README.md) › Module 6 of 8

# Database reliability

Guidelines for keeping data safe and available: backups that are proven to
restore, failover that works, and schema changes that never take a service
down.

*For engineers who own data · About 7 minutes to read · New to a term? See the [glossary](../docs/glossary.md).*

> [!NOTE]
> **In plain language.** A software outage is inconvenient; losing data can be permanent. Records of
> payments, medical appointments or benefits cannot simply be recreated.
> Databases are also where many of the longest outages start, often during a
> routine change. This module sets out the practices that protect data and keep
> databases available: tested backups, automatic switching to a standby
> copy when the main one fails (failover), safe changes and capacity planning.

## On this page

- [1. Availability design](#1-availability-design)
- [2. Backups and recovery](#2-backups-and-recovery)
- [3. Safe schema changes](#3-safe-schema-changes)
- [4. Major-version upgrades](#4-major-version-upgrades)
- [5. Observability](#5-observability)
- [6. Capacity planning](#6-capacity-planning)
- [7. Access and security](#7-access-and-security)
- [Checklist](#checklist)

## 1. Availability design

- **Use a managed database service** (for example Amazon RDS or Aurora,
  Google Cloud SQL, Azure Database) unless there is a strong, documented
  reason not to. The provider runs patching, backups and failover, tested at
  scale; the team still sets retention, schedules maintenance windows and
  major-version upgrades, and proves restores work (section 2).
- **Primary plus standby in a different availability zone**, with automatic
  failover. The standby uses synchronous or storage-level replication;
  asynchronous read replicas can lose recent commits if promoted.
- **Applications reconnect cleanly.** Managed failover usually completes in
  30 to 120 seconds. Do not cache DNS longer than about 30 seconds, set
  connect and query timeouts, and retry with jittered backoff (only for
  idempotent operations, see [event-driven](../event-driven/)). Trigger a
  failover deliberately at least quarterly to prove it works.
- **Read replicas** for read-heavy workloads and reporting, so most of that
  load stays off the primary. Replicas lag behind the primary: never use them
  for reads that must see a write just made. On PostgreSQL, long queries on a
  replica can still cause bloat on the primary or be cancelled; heavy
  analytics belongs in a separate store fed by change data capture.
- **Connection pooling** (for example PgBouncer or the provider's proxy).
  Running out of database connections is one of the most common causes of
  outages under load. Size pools so (maximum application replicas × pool
  size) stays below the database's connection limit, with room for
  administration and failover, and set the autoscaler maximum accordingly
  (see [Kubernetes](../kubernetes/README.md#choosing-an-autoscaler)).
- Set **statement timeouts** and an **idle-in-transaction timeout** (in
  PostgreSQL, `idle_in_transaction_session_timeout`), so a slow query or a
  forgotten open transaction cannot hold locks indefinitely. Application
  timeouts should be shorter than the database's.
- Require TLS for every database connection.

## 2. Backups and recovery

A backup that has never been restored is a hope, not a backup.

| Practice | Standard |
| --- | --- |
| Automated backups | Daily snapshots plus continuous transaction logs (point-in-time recovery) |
| Retention | At least 14 days of point-in-time recovery; periodic snapshots kept longer (for example 90 days), because corruption and ransomware are often found weeks later; longer where regulation requires |
| Isolation | Copies in a separate account and region, protected from deletion (immutable / object lock), encrypted with a key owned by that account. Their RPO is usually the snapshot interval, not point-in-time |
| Encryption | At rest and in transit |
| **Restore testing** | Automated restore to a scratch environment at least monthly; verify row counts and application checks |
| Recovery objectives | RPO and RTO written per database and agreed with the business |
| Recorded drills | Full recovery exercise twice a year, timed against the RTO; at least one a year restores from the isolated copy |

Restore to a new instance next to the damaged one and copy back the affected
data; restoring over the live database discards every write since the restore
point.

## 3. Safe schema changes

Most database incidents are caused by changes, not hardware.

**Expand and contract.** Never make a change that breaks the version of the
application currently running, or the version you might roll back to. Split
it into backward-compatible steps:

1. **Expand:** add the new column or table, nullable or with a constant
   default, so the running version is unaffected.
2. Deploy code that writes to both old and new (still reading old).
3. **Backfill** existing rows in small batches, then verify old and new match.
4. Deploy code that reads from the new structure while still writing both, so
   the previous version stays a safe rollback target.
5. Deploy code that no longer reads or writes the old structure.
6. **Contract:** once no running or rollback version uses it, remove the old
   column or table.

**Rules**

- Every migration is code-reviewed and run in a staging environment with
  production-like data volume first (see [Safe delivery](../safe-delivery/)).
- Run migrations as a separate pipeline step, never on application start-up,
  and take a verified snapshot before any irreversible step.
- Know which operations lock tables in your database engine, and use online
  alternatives:
  - PostgreSQL: `CREATE INDEX CONCURRENTLY` (cannot run inside a transaction;
    if it fails it leaves an invalid index to drop and retry); add constraints
    as `NOT VALID`, then `VALIDATE CONSTRAINT` separately.
  - MySQL: `ALGORITHM=INSTANT` or `INPLACE, LOCK=NONE`, or online schema
    change tools such as gh-ost.
  - Adding a column with a default rewrites the whole table on older engine
    versions (PostgreSQL before 11, MySQL before 8.0.12) or with volatile
    defaults.
- Set a **lock timeout** on migrations (for example `SET lock_timeout = '5s'`
  in PostgreSQL, `lock_wait_timeout` in MySQL, whose default is one year), with
  automatic retry, so they fail fast instead of queueing behind long
  transactions and blocking all traffic.
- Large data changes run in batches with pauses, and can be stopped safely.
- Each migration has a written rollback, or is explicitly marked as
  irreversible with sign-off and a verified backup taken just before.

## 4. Major-version upgrades

Plan upgrades well before the engine version's end of support. Rehearse on a
restored copy of production, use the provider's blue/green deployment or
logical replication for a short cutover, and refresh planner statistics
afterwards.

## 5. Observability

Monitor these for every production database, in addition to the
[observability standard](../observability/):

| Signal | Why |
| --- | --- |
| Connections in use vs. maximum | Exhaustion causes total outage |
| Query latency (p95, p99) and slow query log | First sign of missing indexes or contention |
| Replication lag | Stale reads; risk of data loss on failover |
| Lock waits and deadlocks | Migrations or hot rows blocking traffic |
| Oldest open transaction; idle-in-transaction sessions | Block vacuum, migrations and failover |
| Storage used, growth rate and projected time to full | Full disks stop writes; alert on time to full (for example under 14 days), not only percent used |
| CPU, I/O and IOPS saturation, burst-credit balance | Capacity planning |
| Memory: cache hit ratio, swapping, out-of-memory events | Databases deliberately fill memory with cache, so raw memory use says little |
| Time since last successful backup and last restore test | Proves recoverability; alert on age, not only on failure, because a job that stops running reports no failures |
| Transaction ID and multixact age (PostgreSQL) | Wraparound forces an outage if ignored; alert at about half the limit |
| Replication slot retained WAL (PostgreSQL) | An abandoned slot fills the disk |

## 6. Capacity planning

- Review growth quarterly and project six to twelve months ahead.
- Keep at least 30% headroom at peak on CPU, connections, storage and
  IOPS/throughput. For memory, watch the cache hit ratio, swapping and
  out-of-memory events instead of raw usage.
- Load-test before major launches and seasonal peaks.
- Prefer scaling reads with replicas and caching before scaling the primary
  vertically; plan partitioning before tables become too large to change.

## 7. Access and security

- Applications use dedicated credentials with least privilege, rotated
  automatically.
- No direct human write access to production by default; emergency access is
  time-limited, approved and logged.
- Personal and sensitive data is identified, encrypted and access-audited.

## Checklist

| # | Requirement | Done |
| --- | --- | --- |
| 1 | Managed service (or documented reason), multi-zone, automatic failover | ☐ |
| 2 | Application reconnects cleanly after failover; failover tested at least quarterly | ☐ |
| 3 | Connection pooling sized to the connection limit; statement and idle-in-transaction timeouts | ☐ |
| 4 | Point-in-time recovery; isolated, immutable, longer-retention copies | ☐ |
| 5 | Automated monthly restore test | ☐ |
| 6 | RPO and RTO written and agreed | ☐ |
| 7 | Migrations follow expand and contract, run as a separate step, with lock timeouts | ☐ |
| 8 | Database signals monitored and alerted | ☐ |
| 9 | Capacity reviewed quarterly with 30% headroom | ☐ |
| 10 | Least-privilege, audited access over TLS | ☐ |
| 11 | Major-version upgrades planned before end of support | ☐ |

---

| Previous | Overview | Next |
| :--- | :---: | ---: |
| [← 5. High-availability Kubernetes](../kubernetes/) | [All modules](../README.md#the-eight-modules) | [7. Event-driven systems →](../event-driven/) |
