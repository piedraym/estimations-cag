import structlog
import litellm

from app.config import get_settings
from app.context.examples import ESTIMATION_EXAMPLES, format_examples_for_prompt

log = structlog.get_logger()

MAX_TOKENS = 4000


class LLMServiceError(Exception):
    """Raised when the LLM provider call fails."""


def build_system_prompt() -> str:
    """Construct the system prompt with role definition and reference examples."""
    examples_text = format_examples_for_prompt(ESTIMATION_EXAMPLES)
    return (
        "You are a senior software consultant with 15+ years of experience in project "
        "estimation. Your task is to produce a detailed software project estimation based "
        "on a meeting transcription provided by the user.\n\n"
        "Below are reference estimations from previous projects. Use them as a guide for "
        "structure, level of detail, and realistic pricing. Adapt the content to match the "
        "specific project described in the transcription.\n\n"
        "Your output MUST follow this exact format:\n"
        "- Project title as an H2 heading\n"
        "- A task breakdown table with columns: Task, Hours, Cost (EUR)\n"
        "- Total hours\n"
        "- Total cost in EUR\n"
        "- Recommended team composition\n"
        "- Estimated duration in weeks\n\n"
        "Use a developer rate of approximately 62.50 EUR/hour (500 EUR/day) and a designer "
        "rate of approximately 50 EUR/hour (400 EUR/day). Provide realistic, well-justified "
        "numbers.\n\n"
        f"{examples_text}"
    )


def generate_estimation(transcription: str) -> dict:
    """Generate a software estimation from a meeting transcription using the configured LLM."""
    settings = get_settings()
    system_prompt = build_system_prompt()

    log.info("generating_estimation", model=settings.LLM_MODEL)

    try:
        response = litellm.completion(
            model = settings.LLM_MODEL,
            messages = [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": transcription}
            ],
            max_tokens= MAX_TOKENS
        )

        usage = response.usage
        provider = settings.LLM_MODEL.split("/")[0]

        log.info( 
            "llm_response_received",
            model=response.model,
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
        }

    except LLMServiceError:
        raise
    except Exception as exc:
        log.error("llm_call_failed", error=str(exc), model=settings.LLM_MODEL)
        raise LLMServiceError(f"LLM call failed: {exc}") from exc
