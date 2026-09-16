"""In-memory session state: conversation history + extracted project metadata.

Kept in a plain process dict (no DB/Redis) because at this stage sessions
only need to survive for the lifetime of a single conversation in one
running instance — losing them on restart or across replicas is acceptable
for this phase, and a persistent store would add complexity with no
benefit yet.
"""
from pydantic import BaseModel, Field

MAX_TURNS = 6 # a 'turn' = one user+assistant pair

class ProjectMetadata(BaseModel):
    """Facts about the project accumulated across the conversation."""
    project_name: str | None = None
    assumed_team_size: int | None= None
    mentioned_technologies: list[str] = Field(default_factory=list)
    agreed_scope: str | None= None


class ConversationHistory:
    """Message list with a sliding window over turns.

    The system prompt is not stored as a message here — it's kept
    separate and re-prepended in to_messages_list() so it's never
    evicted by the window logic.
    """
    def __init__(self, max_turns: int = MAX_TURNS):
        self.max_turns = max_turns
        self._turns: list[tuple[dict,dict]] = []  #list of (user_msg, assistant_msg)

    def add_turn(self, user_content: str, assistant_content: str) -> None:
        self._turns.append(
            ({"role": "user", "content": user_content},
             {"role": "assistant", "content": assistant_content})
        )

        if len(self._turns) > self.max_turns:
            self._turns = self._turns[-self.max_turns:]

    def to_messages_list(self, system_promp: str) -> list[dict]:
        messages = [{"role": "system", "content": system_promp}]
        for user_msg, assistant_msg in self._turns:
            messages.append(user_msg)
            messages.append(assistant_msg)
        return messages

class Session:
    """Per-conversation state: history + accumulated project metadata."""

    def __init__(self):
        self.history = ConversationHistory()
        self.metadata = ProjectMetadata()

_sessions: dict[str, Session] = {}

def create_session() -> str:
    import uuid
    session_id = str(uuid.uuid4())
    _sessions[session_id] = Session()
    return session_id

def session_exists(session_id: str) -> bool:
    return session_id in _sessions

def get_session(session_id: str) -> Session:
    return _sessions[session_id]