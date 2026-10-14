# Intentionally unhardened image. Expected findings:
#   DL3006/DL3007 floating base tag, DL3013 unpinned dependency installer,
#   Dockle CIS-DI-0001 running as root, no HEALTHCHECK, old base OS CVEs.
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
