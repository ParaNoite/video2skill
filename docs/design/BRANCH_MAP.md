# Video2Skill Branch Map

All branches start from `main`. They are topic branches only, with no
implementation details baked in.

| Branch | Purpose |
|---|---|
| `feature/source-contract` | Freeze source inspection rules and the source descriptor contract. |
| `feature/task-manifest` | Define task lifecycle, workspace boundaries, and manifest shape. |
| `feature/local-file-ingest` | Cover the local-file entry path and its handoff into task creation. |
| `feature/bilibili-adapter` | Define the Bilibili adapter boundary, capability flags, and disable/recovery behavior. |
| `feature/asr-whispercpp` | Reserve the offline ASR path and its contract with the core pipeline. |
| `feature/ocr-contract` | Define OCR interfaces and the evidence payload they must emit. |
| `feature/evidence-fusion` | Define timeline fusion, source conflict handling, and confidence rules. |
| `feature/knowledge-render` | Define knowledge extraction output and Markdown rendering responsibilities. |
| `feature/local-web-entry` | Define the local web entry surface and its relationship to CLI. |
| `feature/audit-policy` | Define audit rules, evidence gates, and failure reporting. |
| `feature/contract-tests` | Define contract-level smoke tests and regression gates for the above branches. |

Recommended implementation order:

1. `feature/source-contract`
2. `feature/task-manifest`
3. `feature/local-file-ingest`
4. `feature/bilibili-adapter`
5. `feature/asr-whispercpp`
6. `feature/ocr-contract`
7. `feature/evidence-fusion`
8. `feature/knowledge-render`
9. `feature/audit-policy`
10. `feature/local-web-entry`
11. `feature/contract-tests`

