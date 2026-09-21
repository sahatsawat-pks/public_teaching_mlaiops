# ITCS355 — Drill 2 Preparation Guide & Model Q&A

**Course:** ITCS355 Machine Learning Operation and Deployment  
**Session:** Start of Session 3 (Covers Session 2 & Lab 2)  
**Weight:** 3 Marks · 10 Minutes · Closed-book except for student's own repository  
**Student ID:** 6688249  

---

## 1. Drill 2 Structure & Marking Policy

Following the official instructor blueprint (`instructor/drills/README.md` and `RUBRIC-labs-2-to-5.md`), drills are structured into two targeted questions:

| Section | Marks | Focus | Source | Grading Philosophy |
|:---|:---:|:---|:---|:---|
| **Q1 — Concepts** | **2.0** | Core principles from Session 2 | Lecture & Lab 2 concepts | Fast evaluation; partial credit awarded; requires specific mechanisms rather than generic answers. |
| **Q2 — Evidence** | **1.0** | Proof of authentic work | Student's own Lab 2 repo | Binary scoring (matches your submission or scores zero); prevents repository copying. |

---

## 2. Section A: Likely Concept Questions & Model Answers (Q1 · 2 Marks)

Here are the most probable concept questions based on Session 2 slides and instructor rubrics:

### Question Option 1: The 02:00 Incident & Model Lineage
> **Question:** At 02:00 an alert fires in production: predictions are degrading. Why is knowing the F1 or ROC-AUC useless at this moment, and what exact question must model lineage answer? Name the three upstream artifacts linked by lineage.
> 
> **Model Answer:**
> - Performance metrics from training describe historical validation, not why live production inference is currently failing.
> - The essential incident question is: *"Which exact code, which data, and which hyperparameters produced the model artifact currently serving in production?"*
> - The three linked upstream artifacts:
>   1. **Code:** The immutable Git commit SHA.
>   2. **Data:** Content-addressed data fingerprint / DVC hash.
>   3. **Environment/Hyperparameters:** Logged parameters, seed, and base container image digest.

---

### Question Option 2: Experiment Tracking vs. Model Registry
> **Question:** Explain the difference between an Experiment Tracker (e.g., MLflow Tracking) and a Model Registry. Why is registering every run an anti-pattern?
> 
> **Model Answer:**
> - **Experiment Tracking:** A queryable search log of all experimental iterations, hyperparameter trials, failures, and artifacts during research/training.
> - **Model Registry:** A curated, governed store for production release candidates. It enforces versioning, lifecycle stage promotion (e.g., `Staging` -> `Production`), ownership, and audited compliance tags.
> - **Why not register everything:** A registry containing every run degenerates into an uncurated dump folder, defeating governance, making promotion rules meaningless, and hiding production-vetted candidates under experimental noise.

---

### Question Option 3: Cost per Point vs. Highest Metric
> **Question:** In Lab 2 you evaluated trials by `cost_per_point` rather than raw validation score. Give two reasons why the highest-scoring trial in hyperparameter tuning should frequently *not* be promoted to production.
> 
> **Model Answer:**
> 1. **Seed Noise vs. Real Improvement:** The score difference between trials (e.g., 0.826 to 0.843, a spread of ~0.017) is often smaller than the natural variance caused by varying random seeds (~0.035). Claiming a high-ranking model is "better" is simply selecting on random noise.
> 2. **Diminishing Returns & Latency Costs:** Gaining an extra 0.001 ROC-AUC by tripling trees (from 100 to 300) triples training cost and increases production inference latency and memory footprint by 3x. A simpler, shallower model (e.g., `max_depth=4`) is cheaper to retrain, faster to serve, and less prone to overfitting.

---

### Question Option 4: Submit-Time Identity vs. Run-Time Identity
> **Question:** When submitting a training job to managed cloud compute (e.g., GCP Vertex AI CustomJob), the submission often fails on the very first run even though local CLI commands succeeded. Explain the mechanism causing this failure and how it is fixed.
> 
> **Model Answer:**
> - **Mechanism:** The **submit-time identity** (your authenticated user account / developer CLI) has permission to invoke `aiplatform.jobs.create`, but the managed runner executes under a distinct **run-time service agent** (e.g., `service-<PROJECT_NUM>@gcp-sa-aiplatform-cc.iam.gserviceaccount.com`).
> - By default, that runtime service agent lacks IAM permissions to read private resources (such as pulling images from Google Artifact Registry or accessing Cloud Storage buckets).
> - **Fix:** Explicitly grant the required IAM role (e.g., `roles/artifactregistry.reader`) to the cloud provider's runtime service agent.

---

### Question Option 5: Training/Serving Skew
> **Question:** What is training/serving skew, why does it occur silently, and name two architectural defenses against it.
> 
> **Model Answer:**
> - **Definition:** A discrepancy between how features are computed during training and how they are transformed during live inference.
> - **Why silent:** The model still receives inputs and outputs probabilities without syntax errors or runtime exceptions, but the predictions become degraded or meaningless.
> - **Defenses (any two):**
>   1. Single source of feature computation: Shared Python module/package imported by both training and serving pipelines.
>   2. Boundary schema validation: Asserting strict input types and allowable ranges via Pydantic or schema validators in the serving API (`service/schemas.py`).
>   3. Distribution logging: Logging real serving feature distributions and monitoring drift against the training baseline.

---

## 3. Section B: Evidence from Your Submission (Q2 · 1 Mark)

In Section B, the examiner requires exact figures from your Lab 2 submission (`README_LAB02.md`, `reports/lab2-comparison.md`, and `mlflow.db`).

### Item 1: The First Submission Permission Error
* **Question:** What specific error/permission failed when you submitted your managed cloud job, and what was the fix?
* **Your Answer:**
  - **Error:** HTTP 400 permission denied from Vertex AI Custom Job.
  - **Offending Identity:** The runtime service agent `service-821808260643@gcp-sa-aiplatform-cc.iam.gserviceaccount.com`.
  - **Missing Role:** `roles/artifactregistry.reader`.
  - **Action taken:** Granted `roles/artifactregistry.reader` to the service agent on the Artifact Registry repository `itcs355` so Vertex compute could pull the digest-pinned training image.

---

### Item 2: Your Chosen Model & Hyperparameter Configuration
* **Question:** What run ID did you register to the Model Registry, which hyperparameters did it use, and what was its performance?
* **Your Answer:**
  - **Model Name & Version:** `itcs355-6688249` (Version 1 & 2 in `Staging`).
  - **MLflow Run ID:** `55e93760219e4a91943e49f315295814` (Trial 1).
  - **Hyperparameters:** `n_estimators=100`, `max_depth=4`, `min_samples_leaf=5`, `seed=20260101`.
  - **Validation ROC-AUC:** `0.8426`
  - **Test ROC-AUC:** `0.8532`
  - **Cost:** `0.0002` THB on `e2-standard-4` spot instances.

---

### Item 3: Seed Variance vs. Study Spread
* **Question:** What was the measured seed variance for your chosen model configuration, and how did it compare to the spread across your tuning trials?
* **Your Answer:**
  - **Seed Variance (across 5 seeds 20260101–20260105):**
    - Validation ROC-AUC: $0.8556 \pm 0.0126$
    - Test ROC-AUC: $0.8534 \pm 0.0086$
    - Total spread across seeds: $\approx 0.035$
  - **Comparison to Trials:** The spread across all 12 hyperparameter trials was only $\approx 0.0169$ (from 0.8257 to 0.8426). Because the seed variance (~0.035) is wider than the hyperparameter spread (~0.017), claiming trial 0 was definitively superior to trial 1 would be false precision.

---

### Item 4: Retraining Costs
* **Question:** What does your chosen model cost to retrain monthly, and on what infrastructure?
* **Your Answer:**
  - **Cost:** $\approx 0.0002$ THB / month ($<0.003$ THB / year).
  - **Compute Type:** GCP `e2-standard-4` spot instance (rate 1.92 THB/hr, spot discount factor 0.3).

---

### Item 5: The 8 Lineage Tags Recorded in Registry
* **Question:** Name the lineage fields tagged onto your registered model version.
* **Your Answer:**
  1. `git_commit`: `df296eed3963795c9d662c4fe035d3e97fcf9f71`
  2. `data_version`: `422cccb9136e8140`
  3. `mlflow_run_id`: `55e93760219e4a91943e49f315295814`
  4. `training_job_id`: `projects/821808260643/locations/asia-southeast1/customJobs/708691044316741632`
  5. `image_digest`: `asia-southeast1-docker.pkg.dev/itcs355-6688249/itcs355/itcs355-lab1@sha256:7bf9ba12fcfd5227644934e14dfb4b304029a6b6fcb3038f4e867d559d3ef572`
  6. `seed`: `20260101`
  7. `metric_val`: `0.8426`
  8. `metric_test`: `0.8532`

---

## 4. Rapid 60-Second Memory Card

| Key Concept | The One Sentence You Must Write |
|:---|:---|
| **Incident Lineage** | Lineage connects current serving models to exact Git commit, DVC data hash, container digest, and seed so production issues can be traced and reproduced. |
| **First Job Failure** | The runtime service agent (`service-821808260643@gcp-sa-aiplatform-cc...`) lacked `roles/artifactregistry.reader` to pull the Docker image. |
| **Why Not Best Score** | Score differences between trials (~0.017) are smaller than variance across seeds (~0.035), making the "top" trial random noise that costs 3x more compute. |
| **Selected Run ID** | `55e93760` (`n_estimators=100, max_depth=4, min_samples_leaf=5`, val AUC 0.8426, test AUC 0.8532). |
| **Retraining Cost** | 0.0002 THB / month on `e2-standard-4` spot instances. |
| **Skew Defense** | Import feature extraction logic from a single shared package, validate schemas at service boundaries, and log distribution stats. |
