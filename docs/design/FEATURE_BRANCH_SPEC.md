# Video2Skill Workstream Spec

This document defines what each planned workstream is for, what it accepts,
what it produces, and what it must not do. All of it is intended to land on
`main` in the order described in `BRANCH_MAP.md`.

## Shared rules

- Every workstream must stay within the core contract layer.
- Every workstream must define its own inputs, outputs, and non-goals before code
  lands.
- Each workstream must be independently testable.
- Workstreams must not introduce a new source of truth for task state, evidence,
  or knowledge.
- High-risk text such as commands, paths, and version numbers must remain
  evidence-backed.

## Workstream-by-workstream spec

### `source-contract`

Purpose:
- Freeze the source inspection contract.

Inputs:
- Raw local file paths.
- Raw Bilibili URLs.

Outputs:
- Normalized `SourceDescriptor`.
- Capability flags.
- Explicit unsupported-source failure.

Must do:
- Normalize source identity.
- Separate source metadata from downstream task state.

Must not do:
- Download media.
- Create task workspaces.

### `task-manifest`

Purpose:
- Define task lifecycle and workspace boundaries.

Inputs:
- `SourceDescriptor`.
- Runtime/config metadata.

Outputs:
- `TaskManifest`.
- Task workspace path.
- Initial task state.

Must do:
- Record source, state, completed steps, artifacts, warnings, and output dir.
- Define state transitions and rollback markers.

Must not do:
- Parse media.
- Render final content.

### `local-file-ingest`

Purpose:
- Make local-file input enter the pipeline cleanly.

Inputs:
- Existing local file path.

Outputs:
- Validated local source.
- Task creation handoff.

Must do:
- Verify file existence and basic accessibility.
- Route the file into task creation.

Must not do:
- Add platform-specific parsing logic.

### `bilibili-adapter`

Purpose:
- Define the Bilibili adapter boundary and required local media handoff.

Inputs:
- Bilibili URL.

Outputs:
- Adapter capability result.
- Normalized source descriptor or explicit refusal.
- Required local `source_video` artifact staged under the task cache directory.

Must do:
- Allow the adapter to be disabled.
- Return clear unsupported/blocked responses.
- Keep source inspection metadata-only and side-effect free.
- Download public Bilibili sources into the task cache staging directory after task creation.
- Record the downloaded MP4 in `TaskManifest.artifacts`.

Must not do:
- Bypass access control.
- Persist credentials.
- Save cookies, tokens, or authorization material.
- Silently continue with only a remote URL when local video download fails.

### `asr-whispercpp`

Purpose:
- Reserve the offline ASR path.

Inputs:
- Audio artifact or audio-ready source.
- Task profile / runtime profile.

Outputs:
- Time-stamped transcript.
- ASR metadata and confidence markers.

Must do:
- Preserve timestamps.
- Support offline-first execution.

Must not do:
- Depend on commercial APIs for the primary path.

### `ocr-contract`

Purpose:
- Define OCR interfaces and evidence payloads.

Inputs:
- Image frame or frame batch.

Outputs:
- OCR result payload with text, boxes, confidence, and time reference.

Must do:
- Keep OCR as a pluggable capability.

Must not do:
- Bind the project to one OCR engine in the contract layer.

### `evidence-fusion`

Purpose:
- Merge transcript, OCR, and source metadata into a unified evidence timeline.

Inputs:
- Transcript segments.
- OCR results.
- Source metadata.

Outputs:
- Evidence timeline.
- Conflict records.
- Confidence scores.

Must do:
- Preserve competing candidates when sources disagree.
- Track temporal alignment.

Must not do:
- Invent new facts.

### `knowledge-render`

Purpose:
- Turn vetted evidence into structured knowledge and Markdown output.

Inputs:
- Evidence timeline.
- Content profile.
- Template choice.

Outputs:
- Knowledge units.
- Markdown technical document.

Must do:
- Keep every generated knowledge item traceable to evidence.

Must not do:
- Emit unverified commands or steps as facts.

### `audit-policy`

Purpose:
- Define what passes review and what stays flagged.

Inputs:
- Task artifacts.
- Evidence units.
- Knowledge units.

Outputs:
- Audit report.
- Pass/review/block decision.
- Uncertain item list.

Must do:
- Gate high-risk facts behind evidence.
- Mark low-confidence content explicitly.

Must not do:
- Auto-promote weak evidence into final output.

### `local-web-entry`

Purpose:
- Define the local web entry surface.

Inputs:
- Local browser session.
- Task selection / source input.

Outputs:
- Web UI state.
- Requests into the same core pipeline used by CLI.

Must do:
- Reuse core contracts.
- Stay local-only.

Must not do:
- Become a second business-logic implementation.

### `contract-tests`

Purpose:
- Lock the contracts and prevent regressions.

Inputs:
- Core contracts and feature behavior.

Outputs:
- Smoke tests.
- Contract tests.
- Regression checks.

Must do:
- Verify each workstream-level contract independently.
- Protect the shared schema and lifecycle rules.

Must not do:
- Test implementation internals that are not contract-relevant.

## Recommended execution sequence

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
