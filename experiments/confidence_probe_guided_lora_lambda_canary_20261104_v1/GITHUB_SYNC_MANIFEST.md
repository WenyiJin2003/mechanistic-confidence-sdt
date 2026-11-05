# GitHub sync manifest

The GitHub branch contains the complete scientific record for this canary:
source code, tests, frozen data, run configuration and lifecycle records, all
six trained LoRA weight files, free-generation evaluations, randomized blind
packets, raw judge outputs, and the final aggregate and decision records.

The following local-only files are reproducible caches or unchanged upstream
assets and are intentionally not duplicated as Git blobs:

- Python bytecode and pytest caches.
- The identical Qwen2.5-1.5B-Instruct tokenizer bundle copied into each of the
  six adapter directories. Adapter loading should use the base-model revision
  pinned in each `RUN_CONFIG.json` together with the committed adapter weights.

All six local copies have the same hashes:

| Asset | SHA-256 |
|---|---|
| `tokenizer.json` | `9c5ae00e602b8860cbd784ba82a8aa14e8feecec692e7076590d014d7b7fdafa` |
| `vocab.json` | `ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910` |
| `merges.txt` | `8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5` |
| `tokenizer_config.json` | `0a04a9d7d4a62b28482bdfe726c122756de85714fb64166ace92ae75b8f57614` |
| `special_tokens_map.json` | `76862e765266b85aa9459767e33cbaf13970f327a0e88d1c65846c2ddd3a1ecd` |
| `added_tokens.json` | `58b54bbe36fc752f79a24a271ef66a0a0830054b4dfad94bde757d851968060b` |
| `chat_template.jinja` | `cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f` |

No scientific row, adapter weight, evaluation, judgment, failure, or terminal
decision is omitted.
