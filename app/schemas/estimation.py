from pydantic import BaseModel, Field
from enum import Enum

# aqui se valida que la transcripcion tiene al menos 50 caracteres
class ProjectType(str, Enum):
    web_application = "web_application"
    mobile_app = "mobile_app"
    landing_page = "landing_page"

class DetailLevel(str, Enum):
    summary ="summary"
    medium = "medium"
    detailed = "detailed"

class OutputFormat(str, Enum):
    phases_table= "phases_table"
    narrative = "narrative"

class EstimationRequest(BaseModel):
    """Incoming request containing a meeting transcription to estimate."""

    transcription: str = Field(..., min_length=50, description="Meeting transcription text")
    project_type: ProjectType = Field(default=ProjectType.web_application, description="Coarse-grained project category.")
    detail_level: DetailLevel = Field(default=DetailLevel.detailed, description="How deep the estimation should go.")
    output_format: OutputFormat = Field(default=OutputFormat.phases_table, description="Shape of the rendered estimation.")


class TokenUsage(BaseModel):
    """Token consumption details from the LLM call."""

    input_tokens: int
    output_tokens: int
    total_tokens: int

class Phase(BaseModel):
    name: str
    hours: float
    cost_eur: float
    confidence_pct: int | None=None

class EstimationData(BaseModel):
    """ Structured estimation content, parsed from LLM's JSON output"""
    title: str
    phases: list[Phase]
    total_hours: float
    total_cost_eur: float
    team: list[str]
    duration_weeks: float
    narrative: str | None = Field(
        default=None, description="Prose summary, populated when output_format == narrative"
    )


class EstimationResponse(BaseModel):
    """Response containing the generated estimation and metadata."""

    data: EstimationData
    model: str = Field(..., description="LLM model used")
    provider: str = Field(..., description="LLM provider used")
    usage: TokenUsage
    prompt_version: str = Field(..., description="Version of the prompt template used")
    cache_hit: bool = Field(..., description="Whether the LLM response was serverd from cache")