FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

WORKDIR /app

# Capa de dependencias (se cachea si pyproject/uv.lock no cambian)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Codigo de la app
COPY . .
RUN uv sync --frozen

EXPOSE 8000 8501

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
