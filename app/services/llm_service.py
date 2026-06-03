from openai import OpenAI
from app.config import get_settings
from app.context.examples import ALL_ESTIMATION_EXAMPLES

settings = get_settings()
client = OpenAI(api_key= settings.OPENAI_API_KEY)

def build_system_prompt() -> str:
    example_text = format_examples(ALL_ESTIMATION_EXAMPLES)
    return f"""Eres un experto en estimaciones de proyectos software.
    Utiliza los siguientes presupuestos historicos como referencia:
    {example_text}
    Genera una estimacion detallada para el proyecto descrito.
    """

async def generate_estimation(transcription: str) -> dict:
    system_prompt = build_system_prompt()

    response = client.chat.completions.create(
        model = settings.LLM_MODEL,
        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcription}
        ] 
    )

    return {
        "estimation": response.choices[0].message.content,
        "model": settings.LLM_MODEL,
        "provider": settings.LLM_PROVIDER,
    }