from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from core.contracts import SourceDescriptor, TaskManifest, TaskState
from core.orchestrator import TaskOrchestrator
from adapters.local_file.adapter import LocalFileAdapter
from adapters.bilibili.adapter import BilibiliAdapter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="video2skill")
    parser.add_argument("--source", required=True, help="Video URL or local file path")
    parser.add_argument("--output-dir", default="workspace", help="Task output directory")
    return parser


def resolve_source(source: str) -> SourceDescriptor:
    if BilibiliAdapter.can_handle(source):
        return BilibiliAdapter.inspect(source)
    return LocalFileAdapter.inspect(Path(source))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = resolve_source(args.source)
    orchestrator = TaskOrchestrator(output_dir=output_dir)
    manifest = orchestrator.create_task(source)

    manifest_path = output_dir / "task_manifest.json"
    manifest_path.write_text(json.dumps(asdict(manifest), default=str, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"task_id={manifest.task_id}")
    print(f"state={manifest.state}")
    print(f"manifest={manifest_path}")
    return 0
