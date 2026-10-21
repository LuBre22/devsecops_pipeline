# Intentionally unhardened image. Expected findings:
#   DL3006/DL3007 floating base tag, DL3013 unpinned dependency installer,
#   Dockle CIS-DI-0001 running as root, no HEALTHCHECK, old base OS CVEs.
FROM python@sha256:da5aee29682d12a6649f51c8d6f15b87deb3e6c524b923c41d0cb3304d07c913
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
