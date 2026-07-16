import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from adapters.local_file.adapter import LocalFileAdapter
from core.contracts import TaskState
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
            self.assertEqual(manifest.source.location, str(sample.resolve()))
            self.assertEqual(manifest.state, TaskState.ANALYZING)
            self.assertTrue(manifest.output_dir.exists())
            self.assertEqual(manifest.output_dir.parent, tmp_path / "workspace")
