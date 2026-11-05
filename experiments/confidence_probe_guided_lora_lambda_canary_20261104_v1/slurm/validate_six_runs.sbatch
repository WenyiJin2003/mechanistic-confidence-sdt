#!/usr/bin/env bash
#SBATCH --job-name=conf-lambda-validate
#SBATCH --partition=shared
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.err
#SBATCH --export=ALL

set -euo pipefail

: "${LORA_VENV:?Export LORA_VENV to the pinned confidence-LoRA environment}"
: "${OUTPUT_ROOT:?Export the same absolute OUTPUT_ROOT used by the six-task array}"
: "${VALIDATION_OUTPUT:?Export a new absolute VALIDATION_OUTPUT JSON path}"
: "${EVALUATION_MANIFEST:?Export a new absolute EVALUATION_MANIFEST JSON path}"

PROJECT_DIR="${PROJECT_DIR:-$HOME/semantic-entropy-probes-diverse-pairs}"
RUN_DIR="$PROJECT_DIR/experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1"

# Submit with --dependency=afterok:<array_job_id> so partial arrays never validate.
source "$LORA_VENV/bin/activate"
python -u "$RUN_DIR/src/validate_six_runs.py" \
  --output-root "$OUTPUT_ROOT" \
  --matrix "$RUN_DIR/config/SIX_RUN_MATRIX.json" \
  --result-file "$VALIDATION_OUTPUT"

python -u "$RUN_DIR/src/build_evaluation_manifest.py" \
  --training-output-root "$OUTPUT_ROOT" \
  --matrix "$RUN_DIR/config/SIX_RUN_MATRIX.json" \
  --dev-file "$RUN_DIR/data/lora_dev_cf3_113.jsonl" \
  --behavior-file "$RUN_DIR/data/behavior_canary_cue50_46.jsonl" \
  --output "$EVALUATION_MANIFEST"
