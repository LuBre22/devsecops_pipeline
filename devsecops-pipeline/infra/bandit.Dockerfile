ARG PYTHON_IMAGE=python@sha256:1fd55c2f838c4f76262f9eeed899ff9168ea96ac383c61667d6f204325e1f169
FROM ${PYTHON_IMAGE}
COPY bandit-requirements.txt /requirements.txt
RUN python -m pip install --no-cache-dir -r /requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1
