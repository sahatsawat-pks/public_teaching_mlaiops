# ITCS355 — Drill 3: Serving, Latency, and Release Safety

**Course:** ITCS355 Machine Learning Operation and Deployment  
**Session:** Start of Session 4 (Covers Session 3 & Lab 3)  
**Weight:** 3 Marks · 10 Minutes · Closed-book except for student's own repository  
**Student ID:** 6688249  

---

## 1. The Drill 3 Question Paper

Following the exact pattern of Drill 1 and Drill 2:

### Question 1 (Concepts · 2.0 Marks · CLO2, CLO3)

> **Scenario A (Primary Expected Prompt — Health vs. Readiness):**  
> Your container deployment configures both liveness (`/health`) and readiness (`/ready`) probes to return `HTTP 200 OK` as soon as the FastAPI process starts.  
> 
> What goes wrong during a rolling deployment if readiness returns 200 while model weights are still loading into memory, and what should the readiness probe check instead?
>
> *(Alternate Expected Prompt — Latency Percentiles):*  
> A teammate benchmarks an inference endpoint under load and reports an average (mean) latency of 120ms, concluding it comfortably meets an SLA of `p95 < 200ms`.  
> What is fundamentally wrong with using the mean to judge that SLA, and what operational failure is the mean hiding?

---

### Question 2 (Evidence from Your Lab 3 Submission · 1.0 Mark · CLO2, CLO3)

> **Evidence Prompt (Latency & Breaking Concurrency):**  
> From your load-test report (`reports/lab3-load.md`), state your service's **p95 latency at concurrency 10**, and the **concurrency level where your service broke**. What specific resource bottleneck caused it to break?
> 
> *(Alternate Evidence Prompt — Rollback & Blast Radius):*  
> In your Task 4 canary experiment, what **specific metric** revealed the degraded model, how long did **detection** take, and how many **faulty requests** were served before rollback completed?

---

## 2. Model Answers & Grading Rubric

### Question 1 — Model Answers & Rubric

#### If asked about Health vs. Readiness:
* **What goes wrong:**  
  The load balancer / orchestrator (e.g., Kubernetes, Vertex AI, Cloud Run) uses the readiness probe to decide when to route live customer traffic to a newly started container. If `/ready` returns 200 before model weights are deserialized into RAM, the load balancer immediately routes incoming user requests to an uninitialised worker, causing a flood of `500 Internal Server Error` or `503 Service Unavailable` failures for real users during rolling updates.
* **What readiness should check instead:**  
  Readiness must verify that the model artifact is **completely loaded into memory and capable of computing a forward pass** (e.g., running a dummy inference or verifying `model is not None`). `/health` checks if the web process is alive; `/ready` checks if the model can serve.
* **Marking (2.0 Marks):**
  * `1.0 Mark`: Explains that traffic is routed prematurely to an unready model, causing customer-facing 500/503 errors during rolling deployment.
  * `1.0 Mark`: Correctly defines the distinction (health = process running, readiness = model loaded and capable of scoring).

#### If asked about Mean vs. Percentiles:
* **What is wrong with the mean:**  
  The arithmetic mean averages out severe tail latencies, hiding the fact that 5% (or 1%) of requests can be suffering unacceptably slow responses. A mean of 120ms is completely compatible with a p95 of 900ms or 2,000ms.
* **What operational failure it hides:**  
  Queueing delay (requests sitting in the socket backlog), cold starts (container scale-up or idle worker wakeup), or garbage collection pauses. It flatters the developer while 1 in 20 users experience a broken or timed-out service.
* **Marking (2.0 Marks):**
  * `1.0 Mark`: Explains that mean obscures tail distribution.
  * `1.0 Mark`: Identifies queueing / cold-start backlog as the operational reality behind high percentiles.

---

### Question 2 — Exact Evidence for Student 6688249

From your submitted [**`reports/lab3-load.md`**](file:///Users/pks_aito/Desktop/ICT/Subject%20Material/4th%20Year%20%28Senior%29/Specialization/AI%20%28Minor%29/ITCS355%20-%20Machine%20Learning%20Operation%20and%20Deployment/Lab/2026-ITCS355-6688249/reports/lab3-load.md):

#### Answer for Latency & Breaking Concurrency:
* **p95 Latency @ Concurrency 10:** **`934.48 ms`** *(median p50 was 622.73 ms, p99 was 1,286.86 ms; local loopback was 28.84 ms)*.
* **Breaking Concurrency:** **`3 VUs`** over public WAN *(exceeded 150ms target due to international WAN round-trip)*; **`18 VUs`** under local proximity.
* **Bottleneck Cause:** The instance (`n1-standard-2`) has only **2 vCPUs running 2 worker processes**. Any concurrency beyond 2–3 requests forces incoming HTTP connections into the OS socket queue. At 50 VUs, queueing delay spiked p95 latency to **6,822 ms** and degraded throughput from 15.28 rps to 11.33 rps.

#### Answer for Canary Rollback (Task 4):
* **Metric that revealed degradation:** HTTP Error Rate (`predict_failures` threshold `> 0.01`, which spiked to 10% returning HTTP 503).
* **Detection Time:** **`5.15 seconds`** from the first injected error (**`19.84 seconds`** total elapsed from canary traffic start).
* **Rollback Time:** **`1.84 seconds`** to issue traffic shift to 100% V1 (plus ~4 seconds in-flight request drain).
* **Impacted Requests Served:** Exactly **`4 requests`** out of 40 received HTTP 503.

#### Answer for Cost per 1,000 Predictions (Task 5):
* **Cost:** **`$0.00576 USD`** ($\approx 0.201$ THB) per 1,000 predictions.
* **Assumptions:** Calculated on `n1-standard-2` ($0.0950/hr) at **30% average diurnal utilization** (15.28 req/s peak capacity = 16,502 effective requests/hour).

---

## 3. Quick 30-Second Drill 3 Memory Card

| Topic | Key Fact to Write Down |
|:---|:---|
| **Health vs. Readiness** | `/health` checks if Uvicorn is alive; `/ready` checks if the model weights are loaded in memory. Returning 200 prematurely routes user traffic to an empty model, causing 503 errors. |
| **Why Not Mean** | Mean hides the long tail of queueing delays and cold starts. Always report p95 or p99 with concurrency specified. |
| **Breaking Point** | Broke at **3 VUs** over WAN (18 VUs local) because `n1-standard-2` (2 vCPUs) saturated worker threads, causing connection backlog queueing. |
| **p95 @ 10 VUs** | **`934.48 ms`** (Throughput: 15.28 req/s). |
| **Rollback Detection** | Detected in **5.15s** via HTTP 503 rate; rollback took **1.84s**; **4 requests** impacted. |
| **Cost / 1k Requests** | **`$0.00576 USD`** (~0.201 THB) at 30% utilization on `n1-standard-2`. |
