# High-Availability Kubernetes: Reference Architecture and Guidelines

A proven design for running critical services on Kubernetes so that the
failure of a server, a data center or a bad deployment does not become an
outage, plus guidelines for upgrading and migrating platforms safely.

## Summary for non-engineers

Kubernetes is the most widely used open-source system for running software in
the cloud. It can restart failed programs and spread them across many
machines, but only if it is configured correctly. Many organizations adopt it
and still suffer outages because of a handful of common configuration gaps.
This module describes the design and the specific settings that close those
gaps, along with a safe, repeatable method for upgrading or migrating
clusters without interrupting users.

## Reference architecture

![High-availability Kubernetes reference architecture: users reach a load balancer that spreads traffic across three availability zones of one cluster, backed by managed multi-zone data services](reference-architecture.svg)

The cluster's worker nodes run in three availability zones (A, B and C) of the
same region. Each zone holds at least one copy of every service, so losing an
entire zone still leaves two zones serving traffic.

**Principles**

1. **Spread across at least three availability zones.** A zone is one or more
   independent data centers. Losing one zone must not take down the service.
2. **Use the managed control plane** offered by the cloud provider (for
   example Amazon EKS, Google GKE, Azure AKS) rather than running it yourself.
3. **Keep state out of the cluster** where possible. Databases, queues and
   object storage run as managed, multi-zone services. Pods are disposable.
4. **Everything as code.** Clusters are created with infrastructure as code
   (Terraform, OpenTofu, Pulumi or similar). Workloads are deployed through
   GitOps (Argo CD, Flux) so the Git repository is the single source of truth.
5. **Plan for the next cluster.** Design so a whole cluster can be replaced,
   which makes upgrades, migrations and disaster recovery the same routine
   operation.

## Workload configuration checklist

These settings prevent the most common Kubernetes outages. An annotated
example manifest is in [`example-deployment.yaml`](example-deployment.yaml).

| # | Setting | Why |
| --- | --- | --- |
| 1 | **At least 3 replicas** for user-facing services | One replica down for maintenance and one failing still leaves capacity |
| 2 | **Topology spread constraints** across zones and nodes | Prevents all replicas landing in one zone or on one machine |
| 3 | **PodDisruptionBudget** | Stops node upgrades and autoscaling from evicting too many replicas at once |
| 4 | **Readiness probe** | Traffic only reaches pods that are ready to serve |
| 5 | **Liveness probe**, conservative, and never checking dependencies | Restarts stuck processes without causing restart storms when a database is slow |
| 6 | **Startup probe** for slow-starting apps | Prevents liveness checks from killing apps still booting |
| 7 | **CPU and memory requests** on every container; **memory limit** set | Lets the scheduler place pods correctly and prevents one pod starving others |
| 8 | **Graceful shutdown**: handle SIGTERM, `preStop` delay, adequate `terminationGracePeriodSeconds` | Requests in flight finish during deploys instead of failing |
| 9 | **Rolling update** with `maxUnavailable: 0` | Capacity never drops during a deploy |
| 10 | **Horizontal Pod Autoscaler** with a sensible minimum | Absorbs traffic spikes |
| 11 | **Run as non-root, read-only root filesystem, drop capabilities** | Limits the damage of a compromised container |
| 12 | **Immutable image tags or digests** | What is tested is exactly what runs |

## Cluster-level guidelines

- **Node groups** across all zones, with cluster autoscaling (Karpenter or
  Cluster Autoscaler). Keep spare capacity so a lost zone can be rescheduled.
- **Separate system workloads** (ingress, DNS, monitoring) onto dedicated
  nodes so application load cannot starve them.
- **CoreDNS and ingress** scaled for peak and covered by
  PodDisruptionBudgets; DNS failures look like everything failing at once.
- **Network policies** default-deny between namespaces, with explicit allows.
- **Secrets** from a managed secret store, never committed to Git in plain
  text.
- **Admission policies** (Kyverno, OPA Gatekeeper) enforce this checklist
  automatically, so new services cannot skip it.
- **Backups** of cluster configuration are the Git repository; backups of data
  belong to the managed data services (see [Database reliability](../database/)).

## Upgrading and migrating safely

Kubernetes releases a new minor version roughly three times a year and each is
supported for a limited time, so upgrades are routine work, not a project.

**In-place upgrades** (control plane, then node groups) suit minor version
steps when the checklist above is in place:

1. Read the release notes for removed APIs; scan manifests with a tool such as
   `kubent` or `pluto`.
2. Upgrade a non-production cluster first and run it for at least a week.
3. Upgrade the control plane, then add-ons (CNI, DNS, ingress, autoscaler).
4. Roll node groups one zone at a time, watching SLO dashboards between
   steps. PodDisruptionBudgets keep capacity up.

**Blue/green cluster migration** suits large changes: a new cloud account, a
new region, a move from self-managed to managed Kubernetes, or several version
steps at once:

1. Build the new ("green") cluster entirely from code.
2. Deploy all workloads to it through GitOps. Verify with synthetic traffic.
3. Shift real traffic gradually with weighted DNS or the load balancer:
   1% → 10% → 50% → 100%, holding at each step while SLOs stay green.
4. Keep the old ("blue") cluster running and ready for instant rollback until
   the new one has run a full business cycle.
5. Decommission the old cluster.

**Rules for every upgrade or migration**

- Never during peak hours or a change freeze.
- A written rollback plan, tested before starting.
- Stop and roll back if the error budget burn rate crosses the page threshold.
- Record the change so it shows on dashboards.

## Disaster recovery

| Scenario | Design response | Target |
| --- | --- | --- |
| Node failure | Replicas on other nodes; autoscaler replaces the node | No user impact |
| Zone failure | Topology spread, spare capacity, multi-zone data stores | No user impact or brief degradation |
| Bad deployment | Rolling update + automatic rollback on failed health checks or SLO burn | Minutes |
| Cluster failure | Rebuild from code, or fail over to a standby cluster | Defined RTO, tested twice a year |
| Region failure | Standby region for critical services, if business needs justify the cost | Defined RTO/RPO |

RTO (recovery time objective) is how long recovery may take; RPO (recovery
point objective) is how much recent data may be lost. Both are set with the
business and tested with real exercises, not assumed.
