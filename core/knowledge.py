from __future__ import annotations

from core.contracts import EvidenceUnit, KnowledgeUnit


def build_knowledge_outline(evidence: list[EvidenceUnit]) -> list[KnowledgeUnit]:
    outline: list[KnowledgeUnit] = []
    for index, item in enumerate(evidence, start=1):
        outline.append(
            KnowledgeUnit(
                knowledge_id=f"K-{index:04d}",
                type="note",
                title=f"Evidence {index}",
                content=item.content,
                evidence_refs=[item.evidence_id],
                confidence=item.confidence,
            )
        )
    return outline

