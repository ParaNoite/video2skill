# Source Inspection Contract

## Purpose

Source inspection is the first executable step in the pipeline:

`source -> inspect -> task -> evidence -> knowledge -> audit -> output`

It normalizes an incoming user source into a task-safe descriptor, while keeping failure reasons and warnings explicit.

## Inputs

- Local video file path
- Bilibili public video URL or BV ID

Unsupported HTTP(S) URLs must fail before task creation.

## Output

Each adapter returns a `SourceInspection`:

- `available`: whether the source can be used for task creation
- `descriptor`: normalized `SourceDescriptor` when available
- `warnings`: non-blocking issues that should be copied into `TaskManifest.warnings`
- `reason`: blocking failure reason when unavailable

## Rules

- Adapters do not create tasks.
- The CLI creates a task only when `available` is true and `descriptor` is present.
- Bilibili inspection is currently metadata-only and must not require network access.
- Local files may warn on unknown suffixes, but missing paths and directories are blocking failures.

