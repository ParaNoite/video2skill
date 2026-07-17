from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from core.contracts import SourceDescriptor, TaskManifest


FORMAT_POLICY = "best_mp4"
FORMAT_SELECTOR = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
ARTIFACT_KIND = "source_video"
ARTIFACT_FILE_NAME = "source_video.mp4"
STAGING_DIR_NAME = "staging"


class BilibiliDownloadError(RuntimeError):
    pass


class MissingDownloadToolError(BilibiliDownloadError):
    pass


class DownloadCommandError(BilibiliDownloadError):
    pass


def _require_tool(tool_name: str, purpose: str) -> str:
    tool_path = shutil.which(tool_name)
    if tool_path is None:
        raise MissingDownloadToolError(
            f"{tool_name} CLI is required to {purpose}. Install {tool_name} and ensure it is on PATH."
        )
    return tool_path


def _command_error_message(result: subprocess.CompletedProcess[str]) -> str:
    details = (result.stderr or result.stdout or "").strip()
    if details:
        return f"yt-dlp failed to download Bilibili source: {details}"
    return f"yt-dlp failed to download Bilibili source with exit code {result.returncode}"


def download_source_video(
    source: SourceDescriptor,
    manifest: TaskManifest,
    *,
    downloader: str = "yt-dlp",
) -> dict[str, Any]:
    if source.platform != "bilibili":
        raise ValueError(f"Bilibili downloader cannot handle platform: {source.platform}")

    downloader_path = _require_tool(downloader, "download Bilibili videos")
    _require_tool("ffmpeg", "merge Bilibili video and audio streams")

    staging_dir = manifest.cache_dir / STAGING_DIR_NAME
    staging_dir.mkdir(parents=True, exist_ok=True)
    output_path = staging_dir / ARTIFACT_FILE_NAME
    output_template = staging_dir / "source_video.%(ext)s"

    command = [
        downloader_path,
        "--no-playlist",
        "--merge-output-format",
        "mp4",
        "-f",
        FORMAT_SELECTOR,
        "-o",
        str(output_template),
        source.location,
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise MissingDownloadToolError(
            f"{downloader} CLI is required to download Bilibili videos. Install {downloader} and ensure it is on PATH."
        ) from exc

    if result.returncode != 0:
        raise DownloadCommandError(_command_error_message(result))

    if not output_path.is_file():
        raise DownloadCommandError(f"yt-dlp completed but expected MP4 artifact was not created: {output_path}")

    artifact = {
        "kind": ARTIFACT_KIND,
        "platform": "bilibili",
        "path": str(output_path),
        "source_id": source.source_id,
        "canonical_url": source.location,
        "tool": "yt-dlp",
        "format_policy": FORMAT_POLICY,
    }
    manifest.artifacts = [
        existing
        for existing in manifest.artifacts
        if not (
            existing.get("kind") == ARTIFACT_KIND
            and existing.get("platform") == "bilibili"
            and existing.get("source_id") == source.source_id
        )
    ]
    manifest.artifacts.append(artifact)
    if "download_source_video" not in manifest.completed_steps:
        manifest.completed_steps.append("download_source_video")
    return artifact
