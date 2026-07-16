from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4


class TaskState(StrEnum):
    CREATED = "CREATED"
    ANALYZING = "ANALYZING"
    PROCESSING = "PROCESSING"
    REVIEWING = "REVIEWING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass(slots=True)
class SourceDescriptor:
    platform: str
    source_id: str
    title: str
    location: str
    is_local_file: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TaskManifest:
    task_id: str
    source: SourceDescriptor
    state: TaskState
    output_dir: Path
    completed_steps: list[str] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, source: SourceDescriptor, output_dir: Path) -> "TaskManifest":
        return cls(
            task_id=uuid4().hex[:12],
            source=source,
            state=TaskState.CREATED,
            output_dir=output_dir,
        )


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

