# Database Reliability

Guidelines for keeping data safe and available: backups that are proven to
restore, failover that works, and schema changes that never take a service
down.

## Summary for non-engineers

A software outage is inconvenient; losing data can be permanent. Records of
payments, medical appointments or benefits cannot simply be recreated.
Databases are also where many of the longest outages start, often during a
routine change. This module sets out the practices that protect data and keep
databases available: tested backups, automatic failover, safe changes and
capacity planning.

## 1. Availability design

- **Use a managed database service** (for example Amazon RDS or Aurora,
  Google Cloud SQL, Azure Database) unless there is a strong reason not to.
  Patching, backups and failover are then handled by the provider and tested
  at scale.
- **Primary plus standby in a different availability zone**, with automatic
  failover. Applications must reconnect cleanly after a failover (typically
  30 to 120 seconds).
- **Read replicas** for read-heavy workloads and reporting, so analytics
  queries cannot slow down the main application.
- **Connection pooling** (for example PgBouncer or the provider's proxy).
  Running out of database connections is one of the most common causes of
  outages under load.
- Set **statement timeouts** so one slow query cannot hold resources forever.

## 2. Backups and recovery

A backup that has never been restored is a hope, not a backup.

| Practice | Standard |
| --- | --- |
| Automated backups | Daily snapshots plus continuous transaction logs (point-in-time recovery) |
| Retention | At least 14 days; longer where regulation requires |
| Isolation | Copies in a separate account and region, protected from deletion (immutable / object lock) |
| Encryption | At rest and in transit |
| **Restore testing** | Automated restore to a scratch environment at least monthly; verify row counts and application checks |
| Recovery objectives | RPO and RTO written per database and agreed with the business |
| Recorded drills | Full recovery exercise twice a year, timed against the RTO |

## 3. Safe schema changes

Most database incidents are caused by changes, not hardware.

**Expand and contract.** Never make a change that breaks the version of the
application currently running. Split it into backward-compatible steps:

1. **Expand:** add the new column or table (nullable or with a default).
2. Deploy application code that writes to both old and new.
3. **Backfill** existing rows in small batches.
4. Deploy code that reads from the new structure.
5. **Contract:** remove the old column in a later release.

**Rules**

- Every migration is code-reviewed and run in a staging environment with
  production-like data volume first.
- Know which operations lock tables in your database engine. Use online
  alternatives (for example, `CREATE INDEX CONCURRENTLY` in PostgreSQL).
- Set a **lock timeout** on migrations so they fail fast instead of queueing
  behind long transactions and blocking all traffic.
- Large data changes run in batches with pauses, and can be stopped safely.
- Each migration has a written rollback, or is explicitly marked as
  irreversible with sign-off.

## 4. Observability

Monitor these for every production database, in addition to the
[observability standard](../observability/):

| Signal | Why |
| --- | --- |
| Connections in use vs. maximum | Exhaustion causes total outage |
| Query latency (p95, p99) and slow query log | First sign of missing indexes or contention |
| Replication lag | Stale reads; risk of data loss on failover |
| Lock waits and deadlocks | Migrations or hot rows blocking traffic |
| Storage used and growth rate | Full disks stop writes |
| CPU, memory, I/O saturation | Capacity planning |
| Backup success and last restore test | Proves recoverability |
| Transaction ID age (PostgreSQL) | Wraparound forces an outage if ignored |

## 5. Capacity planning

- Review growth quarterly and project six to twelve months ahead.
- Keep at least 30% headroom on CPU, memory, connections and storage at peak.
- Load-test before major launches and seasonal peaks.
- Prefer scaling reads with replicas and caching before scaling the primary
  vertically; plan partitioning before tables become too large to change.

## 6. Access and security

- Applications use dedicated credentials with least privilege, rotated
  automatically.
- No direct human write access to production by default; emergency access is
  time-limited, approved and logged.
- Personal and sensitive data is identified, encrypted and access-audited.

## Checklist

| # | Requirement | Done |
| --- | --- | --- |
| 1 | Managed service, multi-zone, automatic failover | ☐ |
| 2 | Application reconnects cleanly after failover (tested) | ☐ |
| 3 | Connection pooling and statement timeouts | ☐ |
| 4 | Point-in-time recovery, isolated immutable copies | ☐ |
| 5 | Automated monthly restore test | ☐ |
| 6 | RPO and RTO written and agreed | ☐ |
| 7 | Migrations follow expand and contract, with lock timeouts | ☐ |
| 8 | Database signals monitored and alerted | ☐ |
| 9 | Capacity reviewed quarterly with 30% headroom | ☐ |
| 10 | Least-privilege, audited access | ☐ |
