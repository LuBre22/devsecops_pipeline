# Intentionally bad container build. Expected findings:
#   old base image with OS CVEs, root user, secret baked into an ENV layer,
#   package manager cache left in the image, no healthcheck.
FROM alpine:3.9

RUN apk add --no-cache python3

WORKDIR /app
COPY . .

# VULNERABILITY: secret persisted in an image layer (CWE-798).
ENV API_TOKEN="ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"

EXPOSE 8080
CMD ["python3", "app.py"]
