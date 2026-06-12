# HTTP communication is managed here: requests are received, 
# the input format is validated, the work is delegated to the services layer, 
# and the response is then formatted.

import structlog
import json

from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter, HTTPException
from app.schemas.estimation import EstimationRequest, EstimationResponse
from app.services.llm_service import LLMServiceError, generate_estimation, iter_estimation_chunks, start_estimation_stream

log = structlog.get_logger()

router = APIRouter(prefix="/api/v1", tags=["estimations"])

# 1. Receives an HTTP request with the body validated as an EstimationRequest (containing a transcription).
# 2. Delegates the actual work to `generate_estimation()` in the service layer.
# 3. If the LLM service fails, catches the error and returns an HTTP 500 with the error message.
# 4. If successful, returns the response formatted as an EstimationResponse.
@router.post("/estimate")
def create_estimation(request: EstimationRequest) -> EstimationResponse:
    """Receive a meeting transcription and return a software project estimation."""
    try:
        result = generate_estimation(request.transcription)
    except LLMServiceError as exc:
        log.error("estimation_endpoint_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))

    return EstimationResponse(**result)

# llama al modelo en modo streaming, devuelve los trozos (chunk) y los convierte en una representacion json  donde el salto de linea que trae
# en dos caracteres para que quepa en una sola linea 
@router.post("/estimate/stream")
def create_estimation_stream(request: EstimationRequest) -> EventSourceResponse:
    response, cache_hit = start_estimation_stream(request.transcription)

    def event_stream():  # no ejecuta codigo solo crea el objeto para empezar y se detiene (yield)
        for delta in iter_estimation_chunks(response):
            yield {"data": json.dumps(delta)}
    # eventSourceResponde recibe este objeto y pide el siguiente trozo, por cada data que recibe lo convierte en texto plano con formato SSE
    # y lo manda por la conexion HTTP sin esperar el resto.
    return EventSourceResponse(
        event_stream(),
        headers={"X-Cache-Hit": "true" if cache_hit else "false"},
    ) 