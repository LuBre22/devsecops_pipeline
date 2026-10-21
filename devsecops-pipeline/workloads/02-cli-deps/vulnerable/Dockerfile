# Isolated CLI runtime. Legacy Python is deliberate in the negative case.
FROM python@sha256:e191a71397fd61fbddb6712cd43ef9a2c17df0b5e7ba67607128554cd6bff267
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --only-binary=:all: -r requirements.txt
COPY main.py config.yaml ./
USER 10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
CMD ["python", "main.py", "--config", "config.yaml"]
