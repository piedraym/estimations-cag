import structlog
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from app.schemas.estimation import(
    EstimationRequest, EstimationResponse, OpenSession,
    ProjectType, DetailLevel, OutputFormat,
    )
from app.services.sessions import  create_session, session_exists
from app.services.attachments import build_transcript
from app.services.llm_service import generate_estimation, LLMServiceError

log = structlog.get_logger()
router = APIRouter(prefix="/api/v1", tags=["sessions"])

@router.post("/sessions")
def create_session_endpoint() -> OpenSession:
    """Create a empty conversational session and return the identifier."""
    session_id = create_session()
    log.info("Session_created", session_id= session_id)
    return OpenSession(session_id=session_id)

@router.post("/sessions/{session_id}/estimate")
async def create_estimation_with_attachments(
    session_id: str,
    transcript: str = Form(...),
    project_type: ProjectType = Form(default=ProjectType.web_application),
    detail_level: DetailLevel = Form(default= DetailLevel.detailed),
    output_format: OutputFormat = Form(default=OutputFormat.phases_table),
    attachments: list[UploadFile] | None= File(default=None) 
) -> EstimationResponse:
    """Same as POST /estimate, but accepts multipart/form-data with optional
    file attachments whose extracted text is appended to the transcript."""

    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="sesion not found")

    try:
        full_transcript = await build_transcript(transcript, attachments)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    request = EstimationRequest(
        transcription=full_transcript,
        project_type=project_type,
        detail_level=detail_level,
        output_format=output_format,
        session_id= session_id,
    )

    try:
        result = generate_estimation(request)
    except LLMServiceError as exc:
        log.error("estimation_endpoint_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))

    return EstimationResponse(**result)
