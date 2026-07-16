from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar
from uuid import uuid4


class TaskState(StrEnum):
    CREATED = "CREATED"
    ANALYZING = "ANALYZING"
    PROCESSING = "PROCESSING"
    REVIEWING = "REVIEWING"
    DONE = "DONE"
    FAILED = "FAILED"


class SourceCapability(StrEnum):
    LOCAL_MEDIA = "LOCAL_MEDIA"
    REMOTE_REFERENCE = "REMOTE_REFERENCE"
    NETWORK_REQUIRED = "NETWORK_REQUIRED"
    PUBLIC_PLATFORM = "PUBLIC_PLATFORM"


class SourceContractError(ValueError):
    pass


class UnsupportedSourceError(SourceContractError):
    pass


class SourceAccessError(SourceContractError):
    pass


class SourceAdapterDisabledError(SourceContractError):
    pass


@dataclass(slots=True)
class SourceDescriptor:
    platform: str
    source_id: str
    title: str
    location: str
    is_local_file: bool
    capabilities: tuple[SourceCapability, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TaskManifest:
    task_id: str
    source: SourceDescriptor
    state: TaskState
    task_dir: Path
    cache_dir: Path
    output_dir: Path
    completed_steps: list[str] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    _ALLOWED_TRANSITIONS: ClassVar[dict[TaskState, set[TaskState]]] = {
        TaskState.CREATED: {TaskState.ANALYZING},
        TaskState.ANALYZING: {TaskState.PROCESSING, TaskState.FAILED},
        TaskState.PROCESSING: {TaskState.REVIEWING, TaskState.FAILED},
        TaskState.REVIEWING: {TaskState.DONE, TaskState.FAILED},
        TaskState.DONE: set(),
        TaskState.FAILED: set(),
    }

    @classmethod
    def create(
        cls,
        source: SourceDescriptor,
        task_dir: Path,
        cache_dir: Path,
        output_dir: Path,
        task_id: str | None = None,
    ) -> "TaskManifest":
        return cls(
            task_id=task_id or uuid4().hex[:12],
            source=source,
            state=TaskState.CREATED,
            task_dir=task_dir,
            cache_dir=cache_dir,
            output_dir=output_dir,
        )

    def transition_to(self, next_state: TaskState, completed_step: str | None = None) -> None:
        allowed_states = self._ALLOWED_TRANSITIONS[self.state]
        if next_state not in allowed_states:
            raise ValueError(f"Invalid task state transition: {self.state.value} -> {next_state.value}")
        self.state = next_state
        if completed_step is not None and completed_step not in self.completed_steps:
            self.completed_steps.append(completed_step)


@dataclass(slots=True)
class EvidenceUnit:
    evidence_id: str
    time_range: tuple[float, float]
    content: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0


@dataclass(slots=True)
class KnowledgeUnit:
    knowledge_id: str
    type: str
    title: str
    content: str
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass(slots=True)
class AuditReport:
    coverage: float
    conflicts: int
    uncertain_items: int
    decision: str
    notes: list[str] = field(default_factory=list)

def _source_to_dict(source: SourceDescriptor) -> dict[str, Any]:
    return {
        "platform": source.platform,
        "source_id": source.source_id,
        "title": source.title,
        "location": source.location,
        "is_local_file": source.is_local_file,
        "capabilities": [capability.value for capability in source.capabilities],
        "metadata": source.metadata,
    }


def _manifest_to_dict(manifest: TaskManifest) -> dict[str, Any]:
    return {
        "task_id": manifest.task_id,
        "source": _source_to_dict(manifest.source),
        "state": manifest.state.value,
        "task_dir": str(manifest.task_dir),
        "cache_dir": str(manifest.cache_dir),
        "output_dir": str(manifest.output_dir),
        "completed_steps": manifest.completed_steps,
        "artifacts": manifest.artifacts,
        "warnings": manifest.warnings,
    }


def save_manifest(manifest: TaskManifest, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_manifest_to_dict(manifest), ensure_ascii=False, indent=2), encoding="utf-8")


def load_manifest(path: Path) -> TaskManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    source_data = data["source"]
    source = SourceDescriptor(
        platform=source_data["platform"],
        source_id=source_data["source_id"],
        title=source_data["title"],
        location=source_data["location"],
        is_local_file=source_data["is_local_file"],
        capabilities=tuple(SourceCapability(capability) for capability in source_data.get("capabilities", [])),
        metadata=source_data.get("metadata", {}),
    )
    return TaskManifest(
        task_id=data["task_id"],
        source=source,
        state=TaskState(data["state"]),
        task_dir=Path(data["task_dir"]),
        cache_dir=Path(data["cache_dir"]),
        output_dir=Path(data["output_dir"]),
        completed_steps=list(data.get("completed_steps", [])),
        artifacts=list(data.get("artifacts", [])),
        warnings=list(data.get("warnings", [])),
    )
