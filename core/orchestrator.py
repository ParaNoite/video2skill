from __future__ import annotations

from pathlib import Path

from core.contracts import SourceDescriptor, TaskManifest, TaskState


class TaskOrchestrator:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def create_task(self, source: SourceDescriptor) -> TaskManifest:
        task_dir = self.output_dir / source.source_id
        task_dir.mkdir(parents=True, exist_ok=True)
        manifest = TaskManifest.create(source=source, output_dir=task_dir)
        manifest.state = TaskState.ANALYZING
        manifest.completed_steps.append("inspect")
        return manifest

