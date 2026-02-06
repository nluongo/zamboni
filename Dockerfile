FROM python:3.10 AS base

WORKDIR /usr/src/app

COPY src src
COPY docker_run.sh .
COPY pyproject.toml .
COPY README.md .
COPY config.yaml .

RUN pip install .[dbs]

FROM base AS sqlite
COPY config_sqlite.yaml ./config.yaml
CMD ["python", "-m", "zamboni"]

FROM base AS postgres
COPY config_postgres.yaml ./config.yaml
CMD ["python", "-m", "zamboni"]
