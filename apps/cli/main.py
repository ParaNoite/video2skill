from __future__ import annotations

import argparse
import sys
from pathlib import Path

from adapters import inspect_source
from core.contracts import SourceContractError, SourceDescriptor, save_manifest
from core.orchestrator import TaskOrchestrator
from tools.media.bilibili import BilibiliDownloadError, download_source_video


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="video2skill")
    parser.add_argument("--source", required=True, help="Video URL or local file path")
    parser.add_argument("--output-dir", default="workspace", help="Task output directory")
    return parser


def resolve_source(source: str) -> SourceDescriptor:
    return inspect_source(source)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        source = resolve_source(args.source)
        orchestrator = TaskOrchestrator(output_dir=output_dir)
        manifest = orchestrator.create_task(source)

        source_video_artifact = None
        if source.platform == "bilibili":
            source_video_artifact = download_source_video(source, manifest)
            save_manifest(manifest, manifest.task_dir / "task_manifest.json")
    except (SourceContractError, BilibiliDownloadError) as exc:
        print(f"error={exc}", file=sys.stderr)
        return 1

    manifest_path = manifest.task_dir / "task_manifest.json"

    print(f"task_id={manifest.task_id}")
    print(f"state={manifest.state.value}")
    print(f"manifest={manifest_path}")
    if source_video_artifact is not None:
        print(f"source_video={source_video_artifact['path']}")
    return 0
