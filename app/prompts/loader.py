import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from app.prompts.examples import ESTIMATION_EXAMPLES
from app.schemas.estimation import (
    EstimationRequest,
    EstimationResponse,
    TokenUsage, 
    ProjectType,
    DetailLevel,
    OutputFormat
)

PROMPTS_DIR = Path(__file__).parent

_env = Environment(
    loader=FileSystemLoader(PROMPTS_DIR),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=False,
    undefined=StrictUndefined, # caulquier variable que este en el template y no este en el contexto, hace que se rompa la app
)

_env.filters["tojson"] = json.dumps

def render_estimation_prompt(
    request: EstimationRequest,
    version: str = "v1",
) -> tuple[str, str]:
    system = _env.get_template(f"estimation/{version}/system.j2")
    user = _env.get_template(f"estimation/{version}/user.j2")

    context = {
        "project_type": request.project_type.value,
        "detail_level": request.detail_level.value,
        "output_format": request.output_format.value,
        "description": request.transcription,
        "examples": ESTIMATION_EXAMPLES,
    }

    return system.render(**context), user.render(**context)