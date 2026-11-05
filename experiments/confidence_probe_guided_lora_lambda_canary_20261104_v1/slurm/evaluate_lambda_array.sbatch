#!/usr/bin/env bash
#SBATCH --job-name=conf-lambda-eval
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
: "${EVALUATION_MANIFEST:?Export the lifecycle-validated evaluation manifest path}"
: "${EVALUATION_OUTPUT_DIR:?Export a fresh shared evaluation output directory}"

PROJECT_DIR="${PROJECT_DIR:-$HOME/semantic-entropy-probes-diverse-pairs}"
RUN_DIR="$PROJECT_DIR/experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1"

case "${SLURM_ARRAY_TASK_ID}" in
  0) RUN_ID="confident_r000" ;;
  1) RUN_ID="hesitant_r000" ;;
  2) RUN_ID="confident_r005" ;;
  3) RUN_ID="hesitant_r005" ;;
  4) RUN_ID="confident_r010" ;;
  5) RUN_ID="hesitant_r010" ;;
  *) echo "Unexpected array task: ${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac

export HF_HOME="${HF_HOME:-$HOME/hf_cache}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
source "$LORA_VENV/bin/activate"
nvidia-smi

# Submit only after validate_six_runs.sbatch succeeds. This reads dev and the
# behavior canary, never the reserved internal test.
python -u "$RUN_DIR/src/evaluate_adapters.py" \
  --run-manifest "$EVALUATION_MANIFEST" \
  --dev-file "$RUN_DIR/data/lora_dev_cf3_113.jsonl" \
  --behavior-file "$RUN_DIR/data/behavior_canary_cue50_46.jsonl" \
  --output-dir "$EVALUATION_OUTPUT_DIR" \
  --run-id "$RUN_ID" \
  --max-new-tokens 512
