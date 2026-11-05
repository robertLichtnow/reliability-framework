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
example manifest is in [`example-deployment.yaml`](example-deployment.yaml)
(items 1 to 12).

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
| 10 | **Autoscaling with a sensible minimum and maximum**, using KEDA or the Horizontal Pod Autoscaler (see [Choosing an autoscaler](#choosing-an-autoscaler)) | Absorbs traffic spikes without paying for peak capacity all the time |
| 11 | **Run as non-root, read-only root filesystem, drop capabilities** | Limits the damage of a compromised container |
| 12 | **Immutable image tags or digests** | What is tested is exactly what runs |
| 13 | **Many moderately sized nodes, not a few very large ones**; spread pods so no single node holds a large share of any service | Nodes will fail, and they are also replaced routinely (operating system image updates, autoscaler consolidation). Losing or draining a node that holds most of the pods is a dramatic event; losing one of many is routine |
| 14 | **Service mesh with rate limiting** on both incoming traffic (north-south) and service-to-service traffic (east-west) | One noisy client or runaway internal caller cannot overwhelm a service. The mesh also adds mutual TLS, timeouts and retries in one place |
| 15 | **Match the node capacity type to the workload.** User-facing services (web servers, APIs) run on on-demand nodes in dedicated node pools, never on spot instances. Spot capacity is for interruptible work (batch jobs, CI). Limit how often the autoscaler replaces nodes just to repack pods (disruption budgets, consolidation settings) | Spot instances can be reclaimed at any time, causing constant churn for services that must stay up. Dedicated node pools, taints and node selectors keep each workload on the right kind of node |
| 16 | **Spare capacity with low-priority "pause" pods** (overprovisioning) | Placeholder pods hold ready, empty capacity. When real pods need room, the placeholders are evicted instantly and the real pods schedule in seconds, instead of waiting minutes for a new node. Example: [`example-overprovisioning.yaml`](example-overprovisioning.yaml) |

### Choosing an autoscaler

- **KEDA** (Kubernetes Event-driven Autoscaling) is the right default for
  most teams. It scales on the signal that actually reflects demand: queue
  length or message age, stream lag, a Prometheus query (such as request rate
  or latency), a schedule, and dozens of other sources. It can also scale
  idle workloads to zero. Under the hood it drives a standard Horizontal Pod
  Autoscaler, so it adds capability without replacing the built-in mechanism.
- **The plain Horizontal Pod Autoscaler** is enough for simple
  request-driven services where CPU or memory usage tracks load closely.
  It has no extra components to run.

Whichever is used, set a minimum that keeps the service highly available
(item 1) and a maximum that downstream dependencies, such as the database,
can handle.

## Cluster-level guidelines

- **Node groups** across all zones, with cluster autoscaling (Karpenter or
  Cluster Autoscaler). Keep spare capacity so a lost zone can be rescheduled
  (see item 16).
- **Separate system workloads** (ingress, DNS, monitoring) onto dedicated
  nodes so application load cannot starve them.
- **CoreDNS and ingress** scaled for peak and covered by
  PodDisruptionBudgets; DNS failures look like everything failing at once.
- **NodeLocal DNSCache** on every node: a DNS cache running as a DaemonSet
  answers most lookups locally, so pods are shielded from CoreDNS latency,
  overload and packet loss, and CoreDNS handles far less traffic.
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
steps at once. It also applies to the **operators and add-ons that run the
cluster itself**, which can fail every workload at once: a major upgrade of
the node autoscaler (for example Karpenter), replacing the network layer (CNI)
or the service mesh, or changing how ingress works. These are safer done by
building a new cluster with the new setup and shifting traffic than by
changing the running cluster in place.

1. Build the new ("green") cluster entirely from code.
2. Deploy all workloads to it through GitOps. Verify the basics with
   synthetic traffic.
3. Shift real traffic gradually with weighted DNS or the load balancer:
   1% → 10% → 50% → 100%, holding at each step while SLOs stay green. An idle
   green cluster emits no meaningful telemetry, so it is not proven until it
   serves real traffic (see [Safe delivery](../safe-delivery/README.md#core-principle-unobserved-is-unproven)).
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
