# Source Inspection Contract

## Purpose

Source inspection is the first executable step in the pipeline:

`source -> inspect -> task -> evidence -> knowledge -> audit -> output`

It normalizes an incoming user source into a task-safe descriptor, while keeping failure reasons explicit.

## Inputs

- Local video file path
- Bilibili public video URL or BV ID

Unsupported HTTP(S) URLs must fail before task creation.

## Output

Successful inspection returns a normalized `SourceDescriptor`:

- `platform`: adapter namespace such as `local_file` or `bilibili`
- `source_id`: stable normalized source identity
- `title`: display title
- `location`: absolute local path or canonical remote URL
- `is_local_file`: whether downstream steps can read directly from disk
- `capabilities`: source capability flags
- `metadata`: adapter-specific normalized metadata

Blocking failures raise `SourceContractError` subclasses:

- `UnsupportedSourceError`: source shape is outside the supported MVP inputs
- `SourceAccessError`: local source cannot be accessed or is not a file
- `SourceAdapterDisabledError`: adapter is explicitly disabled by configuration

## Rules

- Adapters do not create tasks.
- The CLI creates a task only after inspection returns a `SourceDescriptor`.
- Bilibili inspection is currently metadata-only and must not require network access.
- Missing local paths and directories are blocking failures.
