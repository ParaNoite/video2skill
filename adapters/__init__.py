from __future__ import annotations

from pathlib import Path
from typing import Mapping

from core.contracts import (
    SourceAdapterDisabledError,
    SourceDescriptor,
    UnsupportedSourceError,
)

from adapters.bilibili.adapter import BilibiliAdapter
from adapters.local_file.adapter import LocalFileAdapter


def _is_url(source: str) -> bool:
    return "://" in source


def _looks_like_local_path(source: str) -> bool:
    path = Path(source)
    return (
        path.exists()
        or path.suffix != ""
        or source.startswith((".", "~"))
        or "/" in source
        or "\\" in source
        or len(path.parts) > 1
    )


def _is_enabled(enabled_inputs: Mapping[str, bool] | None, platform: str) -> bool:
    if enabled_inputs is None:
        return True
    return enabled_inputs.get(platform, True)


def inspect_source(
    source: str | Path,
    enabled_inputs: Mapping[str, bool] | None = None,
) -> SourceDescriptor:
    if isinstance(source, Path):
        if not _is_enabled(enabled_inputs, "local_file"):
            raise SourceAdapterDisabledError("Local file input is disabled")
        return LocalFileAdapter.inspect(source)

    candidate = source.strip()
    if BilibiliAdapter.can_handle(candidate):
        if not _is_enabled(enabled_inputs, "bilibili"):
            raise SourceAdapterDisabledError("Bilibili input is disabled")
        return BilibiliAdapter.inspect(candidate)

    if _is_url(candidate):
        raise UnsupportedSourceError(f"Unsupported source: {candidate}")

    if not _looks_like_local_path(candidate):
        raise UnsupportedSourceError(f"Unsupported source: {candidate}")

    if not _is_enabled(enabled_inputs, "local_file"):
        raise SourceAdapterDisabledError("Local file input is disabled")
    return LocalFileAdapter.inspect(Path(candidate))
