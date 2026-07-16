import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from adapters.bilibili.adapter import BilibiliAdapter
from apps.cli.main import main
from core.contracts import SourceCapability, SourceDescriptor, TaskManifest, TaskState, load_manifest, save_manifest
from core.orchestrator import TaskOrchestrator


class TaskManifestTest(unittest.TestCase):
    def make_source(self) -> SourceDescriptor:
        return SourceDescriptor(
            platform="local_file",
            source_id="sample",
            title="sample",
            location=str(Path("sample.mp4")),
            is_local_file=True,
            capabilities=(SourceCapability.LOCAL_MEDIA,),
            metadata={"suffix": ".mp4"},
        )

    def test_valid_state_transition_records_completed_step_once(self) -> None:
        manifest = TaskManifest.create(
            source=self.make_source(),
            task_dir=Path("tasks") / "task-1",
            cache_dir=Path("cache") / "task-1",
            output_dir=Path("output") / "task-1",
        )

        manifest.transition_to(TaskState.ANALYZING, completed_step="inspect")
        manifest.transition_to(TaskState.PROCESSING, completed_step="inspect")

        self.assertEqual(manifest.state, TaskState.PROCESSING)
        self.assertEqual(manifest.completed_steps, ["inspect"])

    def test_invalid_state_transition_raises_without_changing_state(self) -> None:
        manifest = TaskManifest.create(
            source=self.make_source(),
            task_dir=Path("tasks") / "task-1",
            cache_dir=Path("cache") / "task-1",
            output_dir=Path("output") / "task-1",
        )

        with self.assertRaises(ValueError):
            manifest.transition_to(TaskState.DONE)

        self.assertEqual(manifest.state, TaskState.CREATED)
        self.assertEqual(manifest.completed_steps, [])

    def test_terminal_states_cannot_transition(self) -> None:
        source = self.make_source()
        done = TaskManifest(
            task_id="done-task",
            source=source,
            state=TaskState.DONE,
            task_dir=Path("tasks") / "done-task",
            cache_dir=Path("cache") / "done-task",
            output_dir=Path("output") / "done-task",
        )
        failed = TaskManifest(
            task_id="failed-task",
            source=source,
            state=TaskState.FAILED,
            task_dir=Path("tasks") / "failed-task",
            cache_dir=Path("cache") / "failed-task",
            output_dir=Path("output") / "failed-task",
        )

        with self.assertRaises(ValueError):
            done.transition_to(TaskState.FAILED)
        with self.assertRaises(ValueError):
            failed.transition_to(TaskState.ANALYZING)

    def test_manifest_json_round_trip_preserves_paths_state_and_source(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = TaskManifest.create(
                source=self.make_source(),
                task_dir=tmp_path / "tasks" / "task-1",
                cache_dir=tmp_path / "cache" / "task-1",
                output_dir=tmp_path / "output" / "task-1",
            )
            manifest.transition_to(TaskState.ANALYZING, completed_step="inspect")
            manifest.artifacts.append({"kind": "manifest"})
            manifest.warnings.append("low confidence placeholder")

            manifest_path = tmp_path / "tasks" / "task-1" / "task_manifest.json"
            save_manifest(manifest, manifest_path)
            loaded = load_manifest(manifest_path)

            self.assertEqual(loaded.task_id, manifest.task_id)
            self.assertEqual(loaded.state, TaskState.ANALYZING)
            self.assertEqual(loaded.task_dir, manifest.task_dir)
            self.assertEqual(loaded.cache_dir, manifest.cache_dir)
            self.assertEqual(loaded.output_dir, manifest.output_dir)
            self.assertEqual(loaded.source.platform, "local_file")
            self.assertEqual(loaded.source.capabilities, (SourceCapability.LOCAL_MEDIA,))
            self.assertEqual(loaded.source.metadata, {"suffix": ".mp4"})
            self.assertEqual(loaded.completed_steps, ["inspect"])
            self.assertEqual(loaded.artifacts, [{"kind": "manifest"}])
            self.assertEqual(loaded.warnings, ["low confidence placeholder"])

    def test_cli_creates_manifest_under_task_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sample = tmp_path / "sample.mp4"
            sample.write_bytes(b"")
            workspace = tmp_path / "workspace"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = main(["--source", str(sample), "--output-dir", str(workspace)])

            self.assertEqual(result, 0)
            output = stdout.getvalue()
            self.assertIn("state=ANALYZING", output)
            manifest_line = next(line for line in output.splitlines() if line.startswith("manifest="))
            manifest_path = Path(manifest_line.removeprefix("manifest="))
            loaded = load_manifest(manifest_path)

            self.assertEqual(manifest_path, workspace / "tasks" / loaded.task_id / "task_manifest.json")
            self.assertTrue((workspace / "tasks" / loaded.task_id).exists())
            self.assertTrue((workspace / "cache" / loaded.task_id).exists())
            self.assertTrue((workspace / "output" / loaded.task_id).exists())

    def test_bilibili_source_uses_task_id_for_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            source = BilibiliAdapter.inspect("https://www.bilibili.com/video/BV1abc")
            manifest = TaskOrchestrator(output_dir=workspace).create_task(source)

            self.assertFalse(manifest.source.is_local_file)
            self.assertEqual(manifest.task_dir, workspace / "tasks" / manifest.task_id)
            self.assertEqual(manifest.cache_dir, workspace / "cache" / manifest.task_id)
            self.assertEqual(manifest.output_dir, workspace / "output" / manifest.task_id)
            self.assertNotIn("bilibili", manifest.task_dir.name)
            self.assertTrue((manifest.task_dir / "task_manifest.json").exists())
