# Evaluation integration plan

This remains an engineering, post-exposure lambda canary. It does not read the
reserved CF2-193 cohort and cannot produce a confirmatory scientific claim.

1. Train the frozen six-cell array with `slurm/train_lambda_array.sbatch`.
2. Run `src/validate_six_runs.py`; all six lifecycle records and reload checks
   must pass.
3. Run `src/build_evaluation_manifest.py` exactly once. It binds every adapter
   directory and the SHA-256 of its `RUN_CONFIG.json`, reload check, adapter
   config, and adapter weights.
4. Submit `slurm/evaluate_lambda_array.sbatch` as a dependent six-cell array.
   Each task generates all 113 LoRA-dev and 46 behavior-canary answers with
   identical neutral prompts and greedy decoding capped at 512 generated
   tokens. Capped rows are retained and explicitly flagged.
5. Run `src/aggregate_canary.py` only after all six evaluation summaries are
   complete. Its primary packet directly compares confident versus hesitant at
   each ratio. Same-role guided-versus-baseline packets are decomposition only.
6. Obtain blind judgments under `config/BLIND_JUDGE_RESULT_SCHEMA.json`, then
   run `src/score_blind_judgments.py`. Lambda selection uses LoRA-dev only;
   behavior-canary results cannot change the selected ratio.

No step overwrites an existing manifest, generation, aggregation, or scoring
record. A failed or incomplete array is fixed as an engineering failure rather
than silently dropping rows.
