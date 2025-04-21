FROM python:3.10.17-alpine

RUN pip install --upgrade pip

ENV POETRY_VERSION=2.1.2
RUN pip install poetry==${POETRY_VERSION}

WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/
COPY mcp_polaris_ai_datainsight /app/mcp_polaris_ai_datainsight

RUN poetry install --no-root

ENTRYPOINT ["poetry", "run", "python", "-m", "mcp_polaris_ai_datainsight.server"]

