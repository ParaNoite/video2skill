from __future__ import annotations

from core.contracts import KnowledgeUnit


def render_markdown(knowledge: list[KnowledgeUnit]) -> str:
    lines = ["# Knowledge Summary", ""]
    for item in knowledge:
        lines.append(f"## {item.title}")
        lines.append(item.content)
        lines.append("")
    return "\n".join(lines).strip() + "\n"

