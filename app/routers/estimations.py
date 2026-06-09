# HTTP communication is managed here: requests are received, 
# the input format is validated, the work is delegated to the services layer, 
# and the response is then formatted.

import structlog
from fastapi import APIRouter, HTTPException

from app.schemas.estimation import EstimationRequest, EstimationResponse
from app.services.llm_service import LLMServiceError, generate_estimation
from fastapi.responses import StreamingResponse

log = structlog.get_logger()

router = APIRouter(prefix="/api/v1", tags=["estimations"])

# 1. Receives an HTTP request with the body validated as an EstimationRequest (containing a transcription).
# 2. Delegates the actual work to `generate_estimation()` in the service layer.
# 3. If the LLM service fails, catches the error and returns an HTTP 500 with the error message.
# 4. If successful, returns the response formatted as an EstimationResponse.
@router.post("/estimate", response_model=EstimationResponse)
async def create_estimation(request: EstimationRequest) -> EstimationResponse:
    """Receive a meeting transcription and return a software project estimation."""
    try:
        result = generate_estimation(request.transcription)
    except LLMServiceError as exc:
        log.error("estimation_endpoint_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))

    return EstimationResponse(**result)