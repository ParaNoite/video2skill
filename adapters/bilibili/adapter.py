from __future__ import annotations

from core.contracts import SourceDescriptor, SourceInspection


class BilibiliAdapter:
    @staticmethod
    def can_handle(source: str) -> bool:
        return "bilibili.com" in source or source.startswith("BV")

    @staticmethod
    def inspect(source: str) -> SourceInspection:
        if not BilibiliAdapter.can_handle(source):
            return SourceInspection.unavailable("Only Bilibili URLs or BV IDs are supported")

        descriptor = SourceDescriptor(
            platform="bilibili",
            source_id=source.replace("https://", "").replace("http://", "").replace("/", "_"),
            title=source,
            location=source,
            is_local_file=False,
        )
        return SourceInspection.ok(descriptor)
