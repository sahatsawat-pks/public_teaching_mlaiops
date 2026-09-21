# Post-mortem — Temperature Sensor Calibration Offset Incident

**What fired:**  
Drift alert on `temp_c` with PSI = 0.412 (> threshold 0.20), KS = 0.384, at 2026-09-21 10:15:00 UTC.

**True cause:**  
Data drift caused by an upstream sensor re-calibration or sudden shift in plant ambient temperature (+6°C bias on all raw telemetry).

**Retrain, roll back, or no action — and why:**  
No action on the model; do NOT retrain and do NOT roll back. The model is functioning correctly; the fault is upstream data corruption. Retraining on corrupted +6°C biased data would bake bad sensor offsets into the weights and permanently destroy model accuracy. Fix the upstream calibration and backfill data.

**What this would have cost if unnoticed for a week:**  
Over-predicting machine failures by ~35% on healthy machines, triggering unnecessary physical maintenance dispatches costing ~140,000 THB in false alarms.

**How to prevent or detect it faster:**  
Add an upstream data contract range-check on temperature delta between plant intake and exhaust to reject unphysical sudden offsets before data lands in the feature store.