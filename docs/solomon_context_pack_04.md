# Context Pack: Quantized Efficiency

## Current Objective
Implement Joe Packet 04, enforcing runtime quantization and efficiency metrics to ensure the machine remains fast enough to repeat.

## Active Engine Tiering
- `joe_blueprint_queue` (T1_deterministic_for_dry_run)
- `soss_loki_picks` (T1_deterministic)

## Completed Efficiency Steps
- Model weight tracking uses supervised JSON schema (`backend/data/model_weights.json`) with rollback policy.
- Scheduler explicitly gated (`SOLOMON_ENABLE_LOKI_SCHEDULER`).
- Browser configurable url detached from IP logic.
- Reader expansion split from `app.js` into `reader-expansion.js`.
- Engine registry enforces tier classification.

## Next Safe Step
Proceed with Joe Packet 05 for Promotion and SS1.
