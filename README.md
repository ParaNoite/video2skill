# Video2Skill Local Agent

Local-first scaffold for turning instructional videos into structured notes
and Markdown technical docs.

## Current scope

- task manifest and lifecycle model
- local-file and Bilibili source contracts
- evidence, knowledge, and audit core models
- CLI bootstrap for creating a task workspace
- architecture and constraint documents

## Project layout

Matches the Word document's recommended structure:

- `launcher/`
- `apps/`
- `core/`
- `adapters/`
- `tools/`
- `configs/`
- `docs/`
- `models/`
- `templates/`
- `runtime/`
- `tests/`
- `third_party/`

Key docs:

- `docs/design/PROJECT_SPEC.md`
- `docs/design/ARCHITECTURE.md`
- `docs/design/CONSTRAINTS.md`
- `docs/design/SOURCE_INSPECTION.md`

## Quick start

```bash
python -m apps.cli --source .\sample.mp4
```
