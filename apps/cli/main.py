from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from core.contracts import SourceInspection
from core.orchestrator import TaskOrchestrator
from adapters.local_file.adapter import LocalFileAdapter
from adapters.bilibili.adapter import BilibiliAdapter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="video2skill")
    parser.add_argument("--source", required=True, help="Video URL or local file path")
    parser.add_argument("--output-dir", default="workspace", help="Task output directory")
    return parser


def resolve_source(source: str) -> SourceInspection:
    if BilibiliAdapter.can_handle(source):
        return BilibiliAdapter.inspect(source)
    if source.startswith(("http://", "https://")):
        return SourceInspection.unavailable("Only Bilibili URLs are supported in this MVP")

    path = Path(source)
    if path.exists() or path.suffix:
        return LocalFileAdapter.inspect(path)
    return SourceInspection.unavailable(f"Local file does not exist: {path}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    inspection = resolve_source(args.source)
    if not inspection.available or inspection.descriptor is None:
        raise ValueError(inspection.reason or "Source is unavailable")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = inspection.descriptor
    orchestrator = TaskOrchestrator(output_dir=output_dir)
    manifest = orchestrator.create_task(source)
    manifest.warnings.extend(inspection.warnings)

    manifest_path = output_dir / "task_manifest.json"
    manifest_path.write_text(json.dumps(asdict(manifest), default=str, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"task_id={manifest.task_id}")
    print(f"state={manifest.state}")
    print(f"manifest={manifest_path}")
    return 0
