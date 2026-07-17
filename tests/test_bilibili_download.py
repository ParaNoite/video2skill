from __future__ import annotations

import io
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from adapters import inspect_source
from adapters.bilibili.adapter import BilibiliAdapter
from apps.cli.main import main
from core.contracts import SourceAdapterDisabledError, load_manifest
from core.orchestrator import TaskOrchestrator
from tools.media.bilibili import (
    DownloadCommandError,
    MissingDownloadToolError,
    download_source_video,
)


def tool_lookup(tool_name: str) -> str | None:
    tools = {
        "yt-dlp": "C:/tools/yt-dlp.exe",
        "ffmpeg": "C:/tools/ffmpeg.exe",
    }
    return tools.get(tool_name)


class BilibiliDownloadTest(unittest.TestCase):
    def test_downloader_stages_url_as_local_video_and_records_artifact(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            source = BilibiliAdapter.inspect("https://www.bilibili.com/video/BV1Q5411W7RE")
            manifest = TaskOrchestrator(output_dir=workspace).create_task(source)

            def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output_index = command.index("-o") + 1
                output_template = Path(command[output_index])
                output_path = output_template.with_name("source_video.mp4")
                output_path.write_bytes(b"mp4")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            with patch("tools.media.bilibili.shutil.which", side_effect=tool_lookup), patch(
                "tools.media.bilibili.subprocess.run", side_effect=fake_run
            ) as run:
                artifact = download_source_video(source, manifest)

            self.assertEqual(artifact["kind"], "source_video")
            self.assertEqual(artifact["platform"], "bilibili")
            self.assertEqual(artifact["source_id"], source.source_id)
            self.assertEqual(artifact["canonical_url"], source.location)
            self.assertEqual(artifact["tool"], "yt-dlp")
            self.assertEqual(artifact["format_policy"], "best_mp4")
            self.assertEqual(Path(artifact["path"]), manifest.cache_dir / "staging" / "source_video.mp4")
            self.assertTrue(Path(artifact["path"]).is_file())
            self.assertEqual(manifest.artifacts, [artifact])
            self.assertIn("download_source_video", manifest.completed_steps)

            command = run.call_args.args[0]
            self.assertIn("--no-playlist", command)
            self.assertIn("--merge-output-format", command)
            self.assertIn("bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best", command)
            self.assertEqual(command[-1], source.location)

    def test_missing_yt_dlp_raises_clear_error_without_artifact(self) -> None:
        with TemporaryDirectory() as tmp:
            source = BilibiliAdapter.inspect("BV1Q5411W7RE")
            manifest = TaskOrchestrator(output_dir=Path(tmp) / "workspace").create_task(source)

            with patch("tools.media.bilibili.shutil.which", return_value=None), self.assertRaises(
                MissingDownloadToolError
            ) as raised:
                download_source_video(source, manifest)

            self.assertIn("yt-dlp CLI is required", str(raised.exception))
            self.assertEqual(manifest.artifacts, [])
            self.assertNotIn("download_source_video", manifest.completed_steps)

    def test_download_failure_does_not_mark_manifest_complete(self) -> None:
        with TemporaryDirectory() as tmp:
            source = BilibiliAdapter.inspect("BV1Q5411W7RE")
            manifest = TaskOrchestrator(output_dir=Path(tmp) / "workspace").create_task(source)
            failed = subprocess.CompletedProcess(["yt-dlp"], 1, stdout="", stderr="private video")

            with patch("tools.media.bilibili.shutil.which", side_effect=tool_lookup), patch(
                "tools.media.bilibili.subprocess.run", return_value=failed
            ), self.assertRaises(DownloadCommandError) as raised:
                download_source_video(source, manifest)

            self.assertIn("private video", str(raised.exception))
            self.assertEqual(manifest.artifacts, [])
            self.assertNotIn("download_source_video", manifest.completed_steps)

    def test_disabled_bilibili_input_does_not_download(self) -> None:
        with patch("tools.media.bilibili.subprocess.run") as run, self.assertRaises(SourceAdapterDisabledError):
            inspect_source(
                "https://www.bilibili.com/video/BV1Q5411W7RE",
                enabled_inputs={"bilibili": False},
            )

        run.assert_not_called()

    def test_cli_downloads_bilibili_source_and_persists_manifest(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"

            def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output_index = command.index("-o") + 1
                output_template = Path(command[output_index])
                output_template.with_name("source_video.mp4").write_bytes(b"mp4")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            stdout = io.StringIO()
            with patch("tools.media.bilibili.shutil.which", side_effect=tool_lookup), patch(
                "tools.media.bilibili.subprocess.run", side_effect=fake_run
            ), redirect_stdout(stdout):
                result = main(
                    [
                        "--source",
                        "https://www.bilibili.com/video/BV1Q5411W7RE",
                        "--output-dir",
                        str(workspace),
                    ]
                )

            self.assertEqual(result, 0)
            output = stdout.getvalue().splitlines()
            manifest_path = Path(next(line for line in output if line.startswith("manifest=")).removeprefix("manifest="))
            source_video_path = Path(
                next(line for line in output if line.startswith("source_video=")).removeprefix("source_video=")
            )
            loaded = load_manifest(manifest_path)

            self.assertEqual(source_video_path, loaded.cache_dir / "staging" / "source_video.mp4")
            self.assertTrue(source_video_path.is_file())
            self.assertEqual(loaded.artifacts[0]["path"], str(source_video_path))
            self.assertIn("download_source_video", loaded.completed_steps)

    def test_cli_reports_download_failure_as_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with patch("tools.media.bilibili.shutil.which", return_value=None), redirect_stderr(stderr):
                result = main(
                    [
                        "--source",
                        "https://www.bilibili.com/video/BV1Q5411W7RE",
                        "--output-dir",
                        str(Path(tmp) / "workspace"),
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("error=yt-dlp CLI is required", stderr.getvalue())

    def test_bilibili_inspect_does_not_download_or_create_files(self) -> None:
        with TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            with patch("tools.media.bilibili.subprocess.run") as run:
                descriptor = BilibiliAdapter.inspect("BV1Q5411W7RE")
            after = set(Path(tmp).iterdir())

            self.assertEqual(descriptor.platform, "bilibili")
            self.assertEqual(before, after)
            run.assert_not_called()

    def test_local_file_cli_does_not_use_bilibili_downloader(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sample = tmp_path / "sample.mp4"
            sample.write_bytes(b"")
            stdout = io.StringIO()

            with patch("apps.cli.main.download_source_video", Mock()) as downloader, redirect_stdout(stdout):
                result = main(["--source", str(sample), "--output-dir", str(tmp_path / "workspace")])

            self.assertEqual(result, 0)
            self.assertNotIn("source_video=", stdout.getvalue())
            downloader.assert_not_called()


if __name__ == "__main__":
    unittest.main()
