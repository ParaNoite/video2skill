from __future__ import annotations

from hashlib import sha1
from pathlib import Path

from core.contracts import SourceAccessError, SourceCapability, SourceDescriptor


def _source_id_for_path(path: Path) -> str:
    digest = sha1(str(path).encode("utf-8")).hexdigest()[:12]
    return f"local_{digest}"


class LocalFileAdapter:
    @staticmethod
    def inspect(path: Path) -> SourceDescriptor:
        try:
            resolved = path.expanduser().resolve(strict=True)
            if not resolved.is_file():
                raise SourceAccessError(f"Local source is not a file: {path}")
        except SourceAccessError:
            raise
        except OSError as exc:
            raise SourceAccessError(f"Cannot access local source: {path}") from exc

        return SourceDescriptor(
            platform="local_file",
            source_id=_source_id_for_path(resolved),
            title=resolved.stem,
            location=str(resolved),
            is_local_file=True,
            capabilities=(SourceCapability.LOCAL_MEDIA,),
            metadata={
                "file_name": resolved.name,
                "suffix": resolved.suffix.lower(),
            },
        )
