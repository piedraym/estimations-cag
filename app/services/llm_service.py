import structlog
import litellm

from collections.abc import Iterator
from app.config import get_settings
from app.prompts.loader import render_estimation_prompt
from app.schemas.estimation import EstimationRequest, EstimationData
from pydantic import ValidationError

log = structlog.get_logger()

MAX_TOKENS = 4000
PROMPT_VERSION = "v1"


class LLMServiceError(Exception):
    """Raised when the LLM provider call fails."""

# Funcion completa que devuleve la llamada el parseo y el retono
def generate_estimation(request: EstimationRequest) -> dict:
    """Generate a software estimation from a meeting transcription using the configured LLM."""
    settings = get_settings()
    system_prompt, user_prompt = render_estimation_prompt(request, version=PROMPT_VERSION)

    log.info(
        "generating_estimation",
        model=settings.LLM_MODEL,
        fallback=settings.LLM_FALLBACK_MODEL,
    )

    try:
        response = litellm.completion(
            model = settings.LLM_MODEL,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens= MAX_TOKENS,
            num_retries= 2,
            fallbacks=[settings.LLM_FALLBACK_MODEL] if settings.LLM_FALLBACK_MODEL else None,
            caching=True,
            ttl=settings.CACHE_TTL_SECONDS,
            response_format=EstimationData,
        )

        try:
            data = EstimationData.model_validate_json(response.choices[0].message.content)
        except ValidationError as exc:
            log.error("estimation_schema_invalid", error=str(exc), raw=response.choices[0].message.content)
            raise LLMServiceError(f"Model returned invalid estimation JSON: {exc}") from exc

        usage = response.usage
        provider = settings.LLM_MODEL.split("/")[0]
        cache_hit = response._hidden_params.get("cache_hit", False)

        log.info( 
            "llm_response_received",
            model=response.model,
            cache_hit=cache_hit,
            input_tokens = usage.prompt_tokens,
            output_tokens = usage.completion_tokens,
        )

        return{
            "data": data.model_dump(),
            "model": response.model,
            "provider": provider,
            "usage":{
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            },
            "prompt_version": PROMPT_VERSION,
        }

    except LLMServiceError:
        raise
    except Exception as exc:
        log.error("llm_call_failed", error=str(exc), model=settings.LLM_MODEL)
        raise LLMServiceError(f"LLM call failed: {exc}") from exc


def start_estimation_stream(request: EstimationRequest) -> tuple:
    settings = get_settings()
    log.info("generate_estimation_stream", model= settings.LLM_MODEL)
    system_prompt, user_prompt = render_estimation_prompt(request, version=PROMPT_VERSION)

    response = litellm.completion(
        model = settings.LLM_MODEL,
        messages= [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=MAX_TOKENS,
        num_retries=2,
        fallbacks=[settings.LLM_FALLBACK_MODEL] if settings.LLM_FALLBACK_MODEL else None,
        stream=True,
        stream_options={"include_usage": True},
        caching=True,
        ttl=settings.CACHE_TTL_SECONDS,
        response_format=EstimationData
    )

    cache_hit= response._hidden_params.get("cache_hit", False)
    log.info("llm_strean_cache_check", cache_hit=cache_hit, model=settings.LLM_MODEL)
    return response, cache_hit

def iter_estimation_chunks(response)-> Iterator[dict]:
    model = None
    usage = None
    buffer = ""
    try:
        for chunk in response:
            model = getattr(chunk, "model", None) or model
            chunk_usage = getattr(chunk, "usage", None)
            if chunk_usage:
                usage = chunk_usage
            delta = chunk.choices[0].delta.content
            if delta:
                buffer += delta
                yield{"type": "delta", "content": delta}
    except Exception as exc:
        log.error("llm_stream_failed", error=str(exc))
        raise LLMServiceError(f"LLM call failed: {exc}") from exc

    try:
        data = EstimationData.model_validate_json(buffer)
    except ValidationError as exc:
        log.error("estimation_schema_invalid", error=str(exc), raw=buffer)
        yield {"type":"error", "detail":f"Model returned invalid estimation Json: {exc}"}
        return
    
    yield{
        "type": "done",
        "model": model,
        "data" : data.model_dump(),
        "usage": {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        }if usage else None,
        "prompt_version": PROMPT_VERSION,
    }

