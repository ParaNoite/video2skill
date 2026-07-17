from __future__ import annotations

from pathlib import Path

from core.contracts import SourceDescriptor, SourceInspection


SUPPORTED_VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


class LocalFileAdapter:
    @staticmethod
    def inspect(path: Path) -> SourceInspection:
        if not path.exists():
            return SourceInspection.unavailable(f"Local file does not exist: {path}")
        if not path.is_file():
            return SourceInspection.unavailable(f"Local source is not a file: {path}")

        suffix = path.suffix.lower()
        warnings: list[str] = []
        if suffix not in SUPPORTED_VIDEO_SUFFIXES:
            warnings.append(f"Unrecognized video suffix: {suffix or '<none>'}")

        descriptor = SourceDescriptor(
            platform="local_file",
            source_id=path.stem,
            title=path.stem,
            location=str(path.resolve()),
            is_local_file=True,
            metadata={"suffix": suffix},
        )
        return SourceInspection.ok(descriptor, warnings=warnings)
