from __future__ import annotations

from pathlib import Path

from core.contracts import SourceDescriptor


class LocalFileAdapter:
    @staticmethod
    def inspect(path: Path) -> SourceDescriptor:
        if not path.exists():
            raise FileNotFoundError(path)
        return SourceDescriptor(
            platform="local_file",
            source_id=path.stem,
            title=path.stem,
            location=str(path.resolve()),
            is_local_file=True,
            metadata={"suffix": path.suffix.lower()},
        )

