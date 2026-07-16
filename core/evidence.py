from __future__ import annotations

from core.contracts import EvidenceUnit


def merge_evidence(items: list[EvidenceUnit]) -> EvidenceUnit:
    if not items:
        raise ValueError("items must not be empty")
    start = min(item.time_range[0] for item in items)
    end = max(item.time_range[1] for item in items)
    content = "\n".join(item.content for item in items if item.content)
    confidence = sum(item.confidence for item in items) / len(items)
    sources = [source for item in items for source in item.sources]
    return EvidenceUnit(
        evidence_id="merged",
        time_range=(start, end),
        content=content,
        sources=sources,
        confidence=confidence,
    )

