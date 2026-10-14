# Hardened image: pinned slim base, non-root user, healthcheck, no cache.
FROM python:3.12-slim

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y iputils-ping curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Least privilege: the service never needs root.
RUN useradd --system --uid 10001 --no-create-home appuser
USER 10001

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8080/health || exit 1

CMD ["python", "app.py"]
