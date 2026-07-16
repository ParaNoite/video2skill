# Video2Skill Local Agent

Local-first scaffold for turning instructional videos into structured notes,
technical docs, and Skill-ready packages.

## Current scope

- task manifest and lifecycle model
- local-file source adapter
- Bilibili adapter placeholder
- evidence, knowledge, and audit core models
- CLI bootstrap for creating a task workspace

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

## Quick start

```bash
python -m apps.cli --source .\sample.mp4
```

