#!/usr/bin/env bash
#SBATCH --job-name=conf-lambda-aggregate
#SBATCH --partition=shared
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.err
#SBATCH --export=ALL

set -euo pipefail

: "${LORA_VENV:?Export LORA_VENV to the pinned confidence-LoRA environment}"
: "${EVALUATION_MANIFEST:?Export the lifecycle-validated evaluation manifest path}"
: "${EVALUATION_OUTPUT_DIR:?Export the completed six-arm evaluation directory}"
: "${AGGREGATION_OUTPUT_DIR:?Export a fresh aggregation output directory}"

PROJECT_DIR="${PROJECT_DIR:-$HOME/semantic-entropy-probes-diverse-pairs}"
RUN_DIR="$PROJECT_DIR/experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1"

# Submit with --dependency=afterok:<evaluation_array_job_id>.
source "$LORA_VENV/bin/activate"
python -u "$RUN_DIR/src/aggregate_canary.py" \
  --run-manifest "$EVALUATION_MANIFEST" \
  --evaluation-dir "$EVALUATION_OUTPUT_DIR" \
  --output-dir "$AGGREGATION_OUTPUT_DIR"
