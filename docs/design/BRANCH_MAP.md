# Video2Skill Implementation Queue

All implementation now happens on `main`. The items below are logical
workstreams, not long-lived git branches.

| Workstream | Purpose |
|---|---|
| `source-contract` | Freeze source inspection rules and the source descriptor contract. |
| `task-manifest` | Define task lifecycle, workspace boundaries, and manifest shape. |
| `local-file-ingest` | Cover the local-file entry path and its handoff into task creation. |
| `bilibili-adapter` | Define the Bilibili adapter boundary, capability flags, and disable/recovery behavior. |
| `asr-whispercpp` | Reserve the offline ASR path and its contract with the core pipeline. |
| `ocr-contract` | Define OCR interfaces and the evidence payload they must emit. |
| `evidence-fusion` | Define timeline fusion, source conflict handling, and confidence rules. |
| `knowledge-render` | Define knowledge extraction output and Markdown rendering responsibilities. |
| `local-web-entry` | Define the local web entry surface and its relationship to CLI. |
| `audit-policy` | Define audit rules, evidence gates, and failure reporting. |
| `contract-tests` | Define contract-level smoke tests and regression gates for the above workstreams. |

Recommended execution order:

1. `source-contract`
2. `task-manifest`
3. `local-file-ingest`
4. `bilibili-adapter`
5. `asr-whispercpp`
6. `ocr-contract`
7. `evidence-fusion`
8. `knowledge-render`
9. `audit-policy`
10. `local-web-entry`
11. `contract-tests`
