import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from adapters.local_file.adapter import LocalFileAdapter
from core.contracts import TaskState, load_manifest
from core.orchestrator import TaskOrchestrator


class SmokeTest(unittest.TestCase):
    def test_local_file_task_creation(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sample = tmp_path / "sample.mp4"
            sample.write_bytes(b"")

            source = LocalFileAdapter.inspect(sample)
            manifest = TaskOrchestrator(output_dir=tmp_path / "workspace").create_task(source)

            self.assertTrue(manifest.source.is_local_file)
            self.assertEqual(manifest.state, TaskState.ANALYZING)
            self.assertTrue((tmp_path / "workspace" / "tasks" / manifest.task_id).exists())
            self.assertTrue((tmp_path / "workspace" / "cache" / manifest.task_id).exists())
            self.assertTrue((tmp_path / "workspace" / "output" / manifest.task_id).exists())

            manifest_path = manifest.task_dir / "task_manifest.json"
            self.assertTrue(manifest_path.exists())
            self.assertEqual(load_manifest(manifest_path).task_id, manifest.task_id)
