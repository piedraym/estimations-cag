import structlog
import litellm

from collections.abc import Iterator
from app.config import get_settings
from app.prompts.loader import render_estimation_prompt
from app.schemas.estimation import EstimationRequest

log = structlog.get_logger()

MAX_TOKENS = 4000
PROMPT_VERSION = "v1"


class LLMServiceError(Exception):
    """Raised when the LLM provider call fails."""


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
        )

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
            "estimation": response.choices[0].message.content,
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
    )

    cache_hit= response._hidden_params.get("cache_hit", False)
    log.info("llm_strean_cache_check", cache_hit=cache_hit, model=settings.LLM_MODEL)
    return response, cache_hit

def iter_estimation_chunks(response)-> Iterator[dict]:
    model = None
    usage = None
    try:
        for chunk in response:
            model = getattr(chunk, "model", None) or model
            chunk_usage = getattr(chunk, "usage", None)
            if chunk_usage:
                usage = chunk_usage
            delta = chunk.choices[0].delta.content
            if delta:
                yield{"type": "delta", "content": delta}
    except Exception as exc:
        log.error("llm_stream_failed", error=str(exc))
        raise LLMServiceError(f"LLM call failed: {exc}") from exc
    
    yield{
        "type": "done",
        "model": model,
        "usage": {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        }if usage else None,
        "prompt_version": PROMPT_VERSION,
    }

