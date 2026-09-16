import structlog
from fastapi import APIRouter

from app.schemas.estimation import OpenSession
from app.services.sessions import create_session

log = structlog.get_logger()
router = APIRouter(prefix="/api/v1", tags=["sessions"])

@router.post("/sessions")
def create_session_endpoint() -> OpenSession:
    """Create a empty conversational session and return the identifier."""
    session_id = create_session()
    log.info("Session_created", session_id= session_id)
    return OpenSession(session_id=session_id)
