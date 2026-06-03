from pydantic import BaseModel, Field

# aqui se vaida que la transcripcion tiene al menos 50 caracteres
class EstimationRequest(BaseModel):
    transcription: str = Field(
        ...,
        min_legth = 50,
        description = "Transcripcion de la reunion con el cliente"
    )

class EstimationResponse(BaseModel):
    estimation: str
    model: str
    provider: str