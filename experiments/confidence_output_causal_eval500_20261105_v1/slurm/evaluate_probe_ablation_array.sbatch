#!/usr/bin/env bash
#SBATCH --job-name=probe-ablate500
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=0-9%8
#SBATCH --output=slurm-%x-%A_%a.out
#SBATCH --error=slurm-%x-%A_%a.err
#SBATCH --export=ALL

set -euo pipefail

: "${LORA_VENV:?Export the pinned confidence-LoRA environment}"
: "${PROJECT_DIR:?Export the remote project directory}"

EXPERIMENT="$PROJECT_DIR/experiments/confidence_output_causal_eval500_20261105_v1"
LAMBDA_RUN="$PROJECT_DIR/experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1"
PROBE="$PROJECT_DIR/experiments/confidence_probe_scaleup_20261104_v1/results_primary_v1/paired_probe_size_920.npz"
MANIFEST="$LAMBDA_RUN/outputs/lambda_canary_20261104_run01/EVALUATION_MANIFEST.json"

if (( SLURM_ARRAY_TASK_ID < 5 )); then
  RUN_ID="confident_r000"
  SHARD_INDEX="$SLURM_ARRAY_TASK_ID"
else
  RUN_ID="hesitant_r000"
  SHARD_INDEX="$((SLURM_ARRAY_TASK_ID - 5))"
fi

SHARD_LABEL="$(printf '%02d' "$SHARD_INDEX")"
SHARD_FILE="$EXPERIMENT/private_data/direct_eval_shards/EVAL_SHARD_${SHARD_LABEL}.jsonl"
OUTPUT_DIR="$EXPERIMENT/outputs/probe_ablation_generation/$RUN_ID/shard_${SHARD_LABEL}"

export HF_HOME="${HF_HOME:-$HOME/hf_cache}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
source "$LORA_VENV/bin/activate"
nvidia-smi

python -u "$EXPERIMENT/src/run_eval500_shard.py" \
  --authority "$EXPERIMENT/PROBE_ABLATION_AUTHORITY.json" \
  --run-manifest "$MANIFEST" \
  --probe-artifact "$PROBE" \
  --run-id "$RUN_ID" \
  --shard-index "$SHARD_INDEX" \
  --shard-file "$SHARD_FILE" \
  --output-dir "$OUTPUT_DIR"
