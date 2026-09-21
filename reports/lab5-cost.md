# Lab 5 — Cost report

Provider `gcp` · instance `n1-standard-2` · 3.80 THB/hour

## 1. Estimate, made before running
120.00 THB

## 2. Actual, from billing filtered by tag
132.00 THB

## 3. The gap
+12.00 THB (+10.0%)

The +12.00 THB (+10.0%) gap remains well within the course-mandated 20% margin. The overrun was driven by two primary factors:
1. **Extended Endpoint Warm Time During Benchmarking:** The Vertex AI endpoint remained provisioned for 45 minutes longer than initially budgeted while running multi-concurrency `k6` load-test iterations and warm-up cycles.
2. **Unestimated Egress & Container Registry Storage:** Cross-region image pulls between GitHub Actions runners and Google Artifact Registry, along with GCS artifact transfers for multiple pipeline runs, accounted for ~4.20 THB that was omitted from the pre-run compute-only estimate.

## 4. Breakdown by component
| Component | THB | Notes |
|---|---|---|
| Training | 18.50 | Vertex AI CustomJob running `e2-standard-4` spot instances across hyperparameter trials |
| Storage | 4.20 | Google Cloud Storage (telemetry datasets, model weights) & Artifact Registry Docker layers |
| Serving | 98.30 | Vertex AI Endpoint provisioned on machine type `n1-standard-2` for load testing & smoke checks |
| Pipeline | 6.00 | Vertex AI Pipelines DAG orchestration executions |
| Monitoring | 5.00 | Cloud Monitoring custom time-series metrics ingestion and log retention |
| **Total** | **132.00** | **Total spend across all Lab 5 resources (Tagged `course=itcs355, lab=5`)** |

## 5. Cost per 1,000 predictions
Measured throughput: 15.3 req/s

| Utilisation | THB per 1,000 |
|---|---|
| 5% | 1.3816 |
| 25% | 0.2763 |
| 80% | 0.0864 |

We consider **25% utilisation (0.2763 THB per 1,000 predictions)** to be the most realistic long-term operating assumption. Industrial manufacturing telemetry follows diurnal operational shifts where factory floors run full shifts during daytime (high utilisation ~60%) but operate on idle maintenance cycles overnight (~5%), yielding an average diurnal duty cycle near 25%.

Below roughly **0.0010 req/s** (~1 request every 17 minutes), scheduled batch inference is cheaper than keeping this endpoint warm. Our continuous telemetry stream runs at 15.3 req/s, which is well above the break-even point, fully justifying a provisioned real-time endpoint over batch inference.

## 6. One optimisation you applied
| | Before | After |
|---|---|---|
| Configuration | `n1-standard-4` (7.60 THB/hr) | `n1-standard-2` (3.80 THB/hr) |
| THB per 1,000 (at 25% util) | 0.5526 THB | 0.2763 THB |
| Latency p95 | 142.3 ms | 148.6 ms |

**Optimization Analysis:** By right-sizing the serving instance from `n1-standard-4` (4 vCPUs, 15 GB RAM) to `n1-standard-2` (2 vCPUs, 7.5 GB RAM), we achieved an immediate **50.0% reduction in hourly serving compute costs**. The single-row inference memory footprint for our scikit-learn random forest is only ~45 MB, meaning the extra memory of the 4-vCPU instance was completely unutilized. The latency cost was negligible (+6.3 ms on p95), comfortably remaining within our pre-declared SLA budget of $p(95) < 150$ ms.
