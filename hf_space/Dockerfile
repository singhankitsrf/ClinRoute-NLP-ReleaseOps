FROM python:3.11-slim-bookworm
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY hf_space/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY --chown=appuser:appuser . /app
RUN mkdir -p /app/data /app/models /app/evaluation && chown -R appuser:appuser /app
ENV PYTHONPATH=/app/src:/app GRADIO_ANALYTICS_ENABLED=False PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
USER appuser
RUN python scripts/generate_synthetic_data.py --rows 3000 --seed 42 && python training/train_baseline.py --metrics evaluation/candidate_metrics.json && python scripts/model_regression_gate.py --baseline evaluation/baseline_metrics.json --candidate evaluation/candidate_metrics.json
EXPOSE 7860
CMD ["python", "hf_space/app.py"]
