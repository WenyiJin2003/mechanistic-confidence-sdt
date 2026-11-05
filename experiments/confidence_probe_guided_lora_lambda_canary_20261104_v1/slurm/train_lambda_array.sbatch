#!/usr/bin/env bash
#SBATCH --job-name=conf-lambda
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=0-5%6
#SBATCH --output=slurm-%x-%A_%a.out
#SBATCH --error=slurm-%x-%A_%a.err
#SBATCH --export=ALL

set -euo pipefail

: "${LORA_VENV:?Export LORA_VENV to the pinned confidence-LoRA environment}"
: "${OUTPUT_ROOT:?Export a new absolute OUTPUT_ROOT; existing arm directories are refused}"

PROJECT_DIR="${PROJECT_DIR:-$HOME/semantic-entropy-probes-diverse-pairs}"
RUN_DIR="$PROJECT_DIR/experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1"
TRAIN_FILE="$RUN_DIR/data/lora_train_cf200_156.jsonl"
DEV_FILE="$RUN_DIR/data/lora_dev_cf3_113.jsonl"
BEHAVIOR_FILE="$RUN_DIR/data/behavior_canary_cue50_46.jsonl"
CALIBRATION_IDS="$RUN_DIR/config/calibration_ids.json"
PROBE_ARTIFACT="$PROJECT_DIR/experiments/confidence_probe_scaleup_20261104_v1/results_primary_v1/paired_probe_size_920.npz"

case "${SLURM_ARRAY_TASK_ID}" in
  0) ROLE="confident"; RATIO="0.00"; LABEL="confident_r000" ;;
  1) ROLE="hesitant";  RATIO="0.00"; LABEL="hesitant_r000" ;;
  2) ROLE="confident"; RATIO="0.05"; LABEL="confident_r005" ;;
  3) ROLE="hesitant";  RATIO="0.05"; LABEL="hesitant_r005" ;;
  4) ROLE="confident"; RATIO="0.10"; LABEL="confident_r010" ;;
  5) ROLE="hesitant";  RATIO="0.10"; LABEL="hesitant_r010" ;;
  *) echo "Unexpected array task: ${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac

OUTPUT_DIR="$OUTPUT_ROOT/$LABEL"
export HF_HOME="${HF_HOME:-$HOME/hf_cache}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

source "$LORA_VENV/bin/activate"
nvidia-smi

python -u "$RUN_DIR/src/train_lambda_canary.py" \
  --train-file "$TRAIN_FILE" \
  --disjoint-from "$DEV_FILE" \
  --disjoint-from "$BEHAVIOR_FILE" \
  --calibration-ids-file "$CALIBRATION_IDS" \
  --probe-artifact "$PROBE_ARTIFACT" \
  --output-dir "$OUTPUT_DIR" \
  --role "$ROLE" \
  --target-gradient-ratio "$RATIO" \
  --epochs 2 \
  --learning-rate 1e-4 \
  --gradient-accumulation 8 \
  --margin 0.5 \
  --max-length 1024 \
  --seed 20261104
