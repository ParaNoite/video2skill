from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

from core.contracts import SourceCapability, SourceDescriptor, UnsupportedSourceError

_BV_ID_PATTERN = re.compile(r"^BV[0-9A-Za-z]+$")


def _with_default_scheme(candidate: str) -> str:
    lowered = candidate.lower()
    if lowered.startswith("bilibili.com/") or lowered.startswith("www.bilibili.com/"):
        return f"https://{candidate}"
    return candidate


def _is_bilibili_host(host: str) -> bool:
    return host == "bilibili.com" or host.endswith(".bilibili.com")


def _extract_video_id(source: str) -> str:
    candidate = source.strip()
    if _BV_ID_PATTERN.fullmatch(candidate):
        return candidate

    parsed = urlparse(_with_default_scheme(candidate))
    if parsed.scheme not in {"http", "https"}:
        raise UnsupportedSourceError(f"Unsupported source: {source}")
    if not _is_bilibili_host(parsed.netloc.lower()):
        raise UnsupportedSourceError(f"Unsupported source: {source}")

    parts = [part for part in parsed.path.split("/") if part]
    for index, part in enumerate(parts):
        if part == "video" and index + 1 < len(parts):
            video_id = parts[index + 1]
            if _BV_ID_PATTERN.fullmatch(video_id):
                return video_id

    raise UnsupportedSourceError(f"Unsupported Bilibili source: {source}")


def _canonical_url(video_id: str) -> str:
    return urlunparse(("https", "www.bilibili.com", f"/video/{video_id}", "", "", ""))


class BilibiliAdapter:
    @staticmethod
    def can_handle(source: str) -> bool:
        try:
            _extract_video_id(source)
            return True
        except UnsupportedSourceError:
            return False

    @staticmethod
    def inspect(source: str) -> SourceDescriptor:
        video_id = _extract_video_id(source)
        canonical_url = _canonical_url(video_id)
        return SourceDescriptor(
            platform="bilibili",
            source_id=f"bilibili_{video_id}",
            title=video_id,
            location=canonical_url,
            is_local_file=False,
            capabilities=(
                SourceCapability.REMOTE_REFERENCE,
                SourceCapability.NETWORK_REQUIRED,
                SourceCapability.PUBLIC_PLATFORM,
            ),
            metadata={
                "video_id": video_id,
                "canonical_url": canonical_url,
                "input": source.strip(),
            },
        )
