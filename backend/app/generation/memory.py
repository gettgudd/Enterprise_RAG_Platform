"""Memory and conversation history manager (Learn from interactions)."""

from typing import Any
from dataclasses import dataclass, field


@dataclass
class ChatTurn:
    role: str
    content: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    timestamp: str | None = None


class ConversationMemory:
    """Maintains user conversation context and interaction history."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.turns: list[ChatTurn] = []

    def add_user_message(self, message: str) -> None:
        self.turns.append(ChatTurn(role="user", content=message))

    def add_assistant_message(self, message: str, citations: list[dict[str, Any]] | None = None) -> None:
        self.turns.append(ChatTurn(role="assistant", content=message, citations=citations or []))

    def get_history(self, max_turns: int = 10) -> list[dict[str, Any]]:
        return [
            {"role": t.role, "content": t.content, "citations": t.citations}
            for t in self.turns[-max_turns:]
        ]
