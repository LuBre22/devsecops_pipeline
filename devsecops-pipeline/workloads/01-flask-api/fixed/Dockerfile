# Locked supported Alpine/Python base; no apt/curl packages or OS shell installs.
FROM python@sha256:1fd55c2f838c4f76262f9eeed899ff9168ea96ac383c61667d6f204325e1f169
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN adduser -S -u 10001 appuser && mkdir -p /app/data && chown -R 10001 /app
COPY data/ /app/data/
USER 10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_ROOT=/app/data PORT=8080
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=2)" || exit 1
CMD ["python3", "app.py"]
