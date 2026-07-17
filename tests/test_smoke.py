import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from adapters.bilibili.adapter import BilibiliAdapter
from adapters.local_file.adapter import LocalFileAdapter
from apps.cli.main import main, resolve_source
from core.contracts import TaskState
from core.orchestrator import TaskOrchestrator


class SmokeTest(unittest.TestCase):
    def test_local_file_task_creation(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sample = tmp_path / "sample.mp4"
            sample.write_bytes(b"")

            inspection = LocalFileAdapter.inspect(sample)

            self.assertTrue(inspection.available)
            self.assertIsNotNone(inspection.descriptor)
            manifest = TaskOrchestrator(output_dir=tmp_path / "workspace").create_task(inspection.descriptor)

            self.assertTrue(manifest.source.is_local_file)
            self.assertEqual(manifest.state, TaskState.ANALYZING)
            self.assertTrue((tmp_path / "workspace" / "sample").exists())

    def test_missing_local_file_reports_unavailable(self) -> None:
        inspection = LocalFileAdapter.inspect(Path("missing.mp4"))

        self.assertFalse(inspection.available)
        self.assertIsNone(inspection.descriptor)
        self.assertEqual(inspection.reason, "Local file does not exist: missing.mp4")

    def test_bilibili_source_is_inspected_without_network(self) -> None:
        inspection = BilibiliAdapter.inspect("BV1xx411c7mD")

        self.assertTrue(inspection.available)
        self.assertIsNotNone(inspection.descriptor)
        self.assertEqual(inspection.descriptor.platform, "bilibili")
        self.assertFalse(inspection.descriptor.is_local_file)

    def test_unsupported_http_source_is_rejected_before_task_creation(self) -> None:
        inspection = resolve_source("https://example.com/sample.mp4")

        self.assertFalse(inspection.available)
        self.assertIsNone(inspection.descriptor)
        self.assertEqual(inspection.reason, "Only Bilibili URLs are supported in this MVP")

    def test_cli_does_not_create_output_for_unavailable_source(self) -> None:
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "workspace"

            with self.assertRaises(ValueError):
                main(["--source", "https://example.com/sample.mp4", "--output-dir", str(output_dir)])

            self.assertFalse(output_dir.exists())
