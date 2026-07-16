from __future__ import annotations

from core.contracts import AuditReport, KnowledgeUnit


class AuditEngine:
    def run(self, knowledge: list[KnowledgeUnit]) -> AuditReport:
        if not knowledge:
            return AuditReport(coverage=0.0, conflicts=0, uncertain_items=0, decision="blocked")
        uncertain = sum(1 for item in knowledge if item.confidence < 0.7)
        coverage = max(0.0, 1.0 - uncertain / len(knowledge))
        decision = "pass" if uncertain == 0 else "review"
        return AuditReport(
            coverage=coverage,
            conflicts=0,
            uncertain_items=uncertain,
            decision=decision,
        )

