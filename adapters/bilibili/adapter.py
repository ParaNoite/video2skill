from __future__ import annotations

from core.contracts import SourceDescriptor


class BilibiliAdapter:
    @staticmethod
    def can_handle(source: str) -> bool:
        return "bilibili.com" in source or source.startswith("BV")

    @staticmethod
    def inspect(source: str) -> SourceDescriptor:
        return SourceDescriptor(
            platform="bilibili",
            source_id=source.replace("https://", "").replace("http://", "").replace("/", "_"),
            title=source,
            location=source,
            is_local_file=False,
        )

