FROM python:3.10.17-alpine

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "mcp_polaris_ai_datainsight.server"]