# Post-mortem — Temperature Sensor Calibration Bias Incident

Five lines. Lab 4 grades lines 3 and 4 hardest.

**What fired:**
Drift alert on feature `temp_c` with PSI = 0.412 (exceeding threshold 0.20) and KS statistic = 0.384 at 2026-09-21 10:15:02 UTC.

**True cause:**
Upstream data drift caused by sensor re-calibration error or plant ventilation offset, introducing a systematic +6°C bias into raw incoming telemetry while underlying equipment remained physically sound.

**Retrain, roll back, or no action — and why:**
No action on the model; do NOT retrain and do NOT roll back. The model inference logic is healthy; the failure is upstream data corruption. Retraining on corrupted data would bake false sensor biases permanently into the decision trees, destroying predictive fidelity once sensors are fixed. The required action is to hold the deployment, recalibrate the upstream sensor producer, and backfill clean telemetry.

**What this would have cost if unnoticed for a week:**
An estimated 35% artificial surge in machine failure alarms across 240 monitored machines, resulting in approximately 140,000 THB in unnecessary emergency technician callouts and production downtime for healthy hardware.

**How to prevent or detect it faster:**
Deploy an upstream data contract range-assertion on raw sensor inputs and monitor differential telemetry (surface temp minus ambient temp) at the ingestion gateway before data enters feature storage.
