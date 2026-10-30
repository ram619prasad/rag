# Kubernetes Horizontal Pod Autoscaler (HPA)

## Overview

The Horizontal Pod Autoscaler (HPA) automatically adjusts the number of replicas of a Kubernetes workload based on observed metrics. Instead of keeping a fixed number of Pods, HPA increases or decreases the desired replica count as demand changes.

HPA commonly scales Deployments and StatefulSets. It does not directly allocate more CPU or memory to an existing Pod; that is a different type of scaling. Horizontal scaling changes the number of replicas, while vertical scaling changes the resources available to individual replicas.

## How HPA Works

The HPA controller periodically reads metrics, compares their current values with configured targets, and calculates a desired replica count. Metrics can include average CPU utilization, memory-related resource metrics, and supported custom or external metrics.

For CPU utilization, an HPA target might ask Kubernetes to keep the average utilization at 60% of the CPU requests of the relevant Pods. This makes appropriate resource requests important: utilization is measured relative to the requested CPU, not the CPU limit.

### Replica Calculation

A simplified scaling formula is:

```text
desiredReplicas = ceil(currentReplicas * currentMetricValue / desiredMetricValue)
```

Suppose a Deployment currently has four replicas, the observed average CPU utilization is 90%, and the target utilization is 60%:

```text
desiredReplicas = ceil(4 * 90 / 60)
                = ceil(6)
                = 6
```

The controller would calculate six desired replicas before applying other HPA rules and safeguards. In real clusters, tolerance, metric readiness, stabilization, and configured scaling policies can influence the final scaling action.

## HPA During Rolling Updates

During a rolling update of a Deployment, the HPA manages the desired replica count on the **Deployment**. The **Deployment controller** manages the underlying ReplicaSets and distributes replicas across them while the rollout progresses.

This separation matters: HPA does not individually scale each ReplicaSet during a Deployment rollout. It updates the workload's desired replicas, and the Deployment controller coordinates how those replicas are realized across the old and new ReplicaSets.

A StatefulSet works differently because it manages its Pods directly rather than through Deployment ReplicaSets. An HPA targeting a StatefulSet adjusts that StatefulSet's desired replica count.

## Scaling Stability and Flapping

Workload demand can fluctuate from minute to minute. If an autoscaler reacted aggressively to every small metric change, the replica count could repeatedly rise and fall. This behavior is often called **flapping** or **thrashing**.

HPA supports stabilization and scaling behavior policies to reduce unnecessary changes. For example, scale-down stabilization can delay a reduction in replicas after a recent period of higher demand, helping avoid rapid oscillation.

Scaling decisions are also affected by tolerance around the target metric. If a change is sufficiently small, the controller may leave the replica count unchanged rather than scaling repeatedly.

## Minimum and Maximum Replicas

An HPA typically specifies a minimum and a maximum replica count. These bounds help keep the workload within an acceptable operating range.

For example, a workload with `minReplicas: 2` and `maxReplicas: 10` is configured to scale within those limits under normal HPA operation. Even if a metric suggests more replicas, the controller will not choose a desired count above the configured maximum.

## Example HPA Configuration

The following simplified manifest targets a Deployment named `orders-api` and aims for an average CPU utilization of 60%.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orders-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orders-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
```

This configuration assumes that the targeted Pods have suitable CPU requests and that the cluster provides the necessary metrics. The manifest alone does not guarantee correct autoscaling if metrics collection or resource-request configuration is missing.

## Troubleshooting Checklist

If HPA is not scaling as expected, inspect the HPA resource and its reported conditions, targets, and events:

```bash
kubectl get hpa
kubectl describe hpa orders-api-hpa
```

Common things to investigate include:

- Whether the metrics pipeline is available and reporting data.
- Whether the Pods specify CPU requests when using CPU utilization targets.
- Whether `minReplicas` or `maxReplicas` is constraining the result.
- Whether scaling policies or stabilization windows are delaying an action.
- Whether the target Deployment or StatefulSet exists and is healthy.

## Key Takeaways

- HPA changes the **number of replicas** based on metrics.
- The replica formula compares the observed metric with its target.
- During Deployment rolling updates, **HPA controls the Deployment replica count**, while the **Deployment controller manages ReplicaSets**.
- Stabilization and tolerance help prevent repeated scale-up and scale-down decisions.
- CPU requests and the metrics pipeline are important for CPU-utilization-based HPA.

> **Learning note:** This is an educational document for Project 00. The replica calculation is simplified; actual scaling depends on Kubernetes configuration and metrics.
