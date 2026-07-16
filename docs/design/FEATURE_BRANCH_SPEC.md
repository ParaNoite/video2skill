# Video2Skill Feature Branch Spec

This document defines what each planned branch is for, what it accepts, what it
produces, and what it must not do.

## Shared rules

- Every feature branch must stay within the core contract layer.
- Every branch must define its own inputs, outputs, and non-goals before code
  lands.
- Each branch must be independently testable.
- Branches must not introduce a new source of truth for task state, evidence,
  or knowledge.
- High-risk text such as commands, paths, and version numbers must remain
  evidence-backed.

## Branch-by-branch spec

### `feature/source-contract`

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

### `feature/task-manifest`

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

### `feature/local-file-ingest`

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

### `feature/bilibili-adapter`

Purpose:
- Define the Bilibili adapter boundary.

Inputs:
- Bilibili URL.

Outputs:
- Adapter capability result.
- Normalized source descriptor or explicit refusal.

Must do:
- Allow the adapter to be disabled.
- Return clear unsupported/blocked responses.

Must not do:
- Bypass access control.
- Persist credentials.

### `feature/asr-whispercpp`

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

### `feature/ocr-contract`

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

### `feature/evidence-fusion`

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

### `feature/knowledge-render`

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

### `feature/audit-policy`

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

### `feature/local-web-entry`

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

### `feature/contract-tests`

Purpose:
- Lock the contracts and prevent regressions.

Inputs:
- Core contracts and feature behavior.

Outputs:
- Smoke tests.
- Contract tests.
- Regression checks.

Must do:
- Verify each branch-level contract independently.
- Protect the shared schema and lifecycle rules.

Must not do:
- Test implementation internals that are not contract-relevant.

## Recommended branch sequence

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

