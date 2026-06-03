# Aqui se gestiona la comunicacion HTTP, se reciben peticiones, se valida el formato de entrada, se delega el trabajo a la capa de servicios
# se formatea la respuesta

from fastapi import APIRouter, Depends
from app.schemas.estimation import EstimationRequest, EstimationResponse
from app.services.llm_service import generate_estimation

router = APIRouter(prefix="/api/v1", tags=["estimations"])

@router.post("/estimate", response_model = EstimationResponse)
async def estimate(request: EstimationRequest):
    result = await generate_estimation(request.transcription)
    return result