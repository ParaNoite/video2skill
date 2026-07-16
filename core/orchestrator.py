from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from core.contracts import SourceDescriptor, TaskManifest, TaskState, save_manifest


class TaskOrchestrator:
    def __init__(self, output_dir: Path) -> None:
        self.workspace_dir = output_dir

    def create_task(self, source: SourceDescriptor) -> TaskManifest:
        task_id = uuid4().hex[:12]
        task_dir = self.workspace_dir / "tasks" / task_id
        cache_dir = self.workspace_dir / "cache" / task_id
        output_dir = self.workspace_dir / "output" / task_id

        for path in (task_dir, cache_dir, output_dir):
            path.mkdir(parents=True, exist_ok=True)

        manifest = TaskManifest.create(
            source=source,
            task_id=task_id,
            task_dir=task_dir,
            cache_dir=cache_dir,
            output_dir=output_dir,
        )
        manifest.transition_to(TaskState.ANALYZING, completed_step="inspect")
        save_manifest(manifest, task_dir / "task_manifest.json")
        return manifest
