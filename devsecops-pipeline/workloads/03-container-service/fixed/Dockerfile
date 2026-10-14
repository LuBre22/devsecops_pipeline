# Hardened container build: current pinned base, non-root, no secrets,
# read-only friendly, explicit healthcheck.
FROM alpine:3.20

RUN apk add --no-cache python3 curl \
    && adduser -S -u 10001 appuser

WORKDIR /app
COPY app.py .
RUN mkdir -p /app/data && chown -R 10001 /app

USER 10001

# No secret in any layer: API_TOKEN is injected at runtime.
ENV DATA_ROOT=/app/data PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8080/health || exit 1

CMD ["python3", "app.py"]
