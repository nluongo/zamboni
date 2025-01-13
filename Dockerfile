FROM python:3.10

WORKDIR /app

COPY ./src ./src
COPY ./scripts ./scripts
COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md

RUN mkdir data
RUN pip install .
