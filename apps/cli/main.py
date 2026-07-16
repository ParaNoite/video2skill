from __future__ import annotations

import argparse
from pathlib import Path

from core.contracts import SourceDescriptor
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
    path = Path(source)
    if path.exists():
        return LocalFileAdapter.inspect(path)
    if source.startswith(("http://", "https://")):
        raise ValueError("Only Bilibili URLs are supported in this MVP")
    raise FileNotFoundError(path)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = resolve_source(args.source)
    orchestrator = TaskOrchestrator(output_dir=output_dir)
    manifest = orchestrator.create_task(source)

    manifest_path = manifest.task_dir / "task_manifest.json"

    print(f"task_id={manifest.task_id}")
    print(f"state={manifest.state.value}")
    print(f"manifest={manifest_path}")
    return 0
