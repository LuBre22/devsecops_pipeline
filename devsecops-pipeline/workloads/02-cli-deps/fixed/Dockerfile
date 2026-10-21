# Isolated CLI runtime. Legacy Python is deliberate in the negative case.
FROM python@sha256:1fd55c2f838c4f76262f9eeed899ff9168ea96ac383c61667d6f204325e1f169
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --only-binary=:all: -r requirements.txt
COPY main.py config.yaml ./
USER 10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
CMD ["python", "main.py", "--config", "config.yaml"]
