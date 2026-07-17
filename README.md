# Video2Skill Local Agent

Local-first scaffold for turning instructional videos into structured notes
and Markdown technical docs.

## Current scope

- task manifest and lifecycle model
- local-file source contracts and Bilibili public-video download handoff
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
- `docs/design/BRANCH_MAP.md` for the mainline execution order
- `docs/design/FEATURE_BRANCH_SPEC.md` for the workstream contract details

## Quick start

```bash
python -m apps.cli --source .\sample.mp4
```

Bilibili sources require the `yt-dlp` CLI and `ffmpeg` on `PATH`. Public videos
are downloaded into the task cache staging directory as `source_video.mp4` and
recorded in the task manifest artifacts before the task can continue.
