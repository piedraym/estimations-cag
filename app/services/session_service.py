import uuid

_session: dict[str, list] = {}

def create_session() -> str:
    session_id = str(uuid.uuid4())
    _session[session_id] = []
    return session_id

def session_exists(session_id: str) -> bool:
    return session_id in _session