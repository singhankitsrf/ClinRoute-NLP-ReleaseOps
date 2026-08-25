FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MODEL_DIR=/models/baseline
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY pyproject.toml README.md ./
COPY src ./src
COPY models /models
RUN python -m pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
USER appuser
EXPOSE 8000
CMD ["uvicorn","clinroute.api:app","--host","0.0.0.0","--port","8000"]
