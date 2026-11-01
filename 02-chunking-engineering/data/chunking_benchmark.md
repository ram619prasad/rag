
# Payment Platform Engineering Handbook

## PostgreSQL Replication

PostgreSQL replication improves database availability by maintaining copies of the primary database. A replica continuously receives and applies changes from the primary server.

Replication lag measures how far a replica is behind the primary database. If replication lag exceeds 30 seconds, engineers should inspect network latency, disk throughput, and long-running transactions before considering a replica restart.

## Kubernetes Autoscaling

The Horizontal Pod Autoscaler automatically adjusts the number of application replicas based on metrics such as CPU utilization, memory usage, or custom application metrics.

If CPU utilization remains above 80 percent, the autoscaler may increase the number of replicas. Scaling behavior depends on configured policies, stabilization windows, and available cluster capacity.

## Incident Response

During a payment service incident, engineers should first identify the affected service, inspect recent deployments, and correlate errors using request identifiers.

If PostgreSQL replication lag is the primary problem, engineers should verify replica health, investigate database resource saturation, and avoid restarting replicas without understanding the cause.

## Rate Limiting

The API gateway applies rate limits to protect backend services from excessive traffic. Different endpoints may have different quotas based on user tier and operational requirements.

A distributed rate limiter must consider concurrent requests, regional availability, counter consistency, and the behavior of clients when limits are exceeded.
