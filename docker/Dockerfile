# Multistage dockerfile

# Base image with build deps
FROM python:3.9-slim AS base

ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.1.5 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    POETRY=/opt/poetry/bin/poetry

ARG PROJECTDIR=api_demo_v3

ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PATH="/${PROJECTDIR}/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /${PROJECTDIR}

COPY ./${PROJECTDIR}/poetry.lock ./${PROJECTDIR}/pyproject.toml ./

RUN poetry install --no-dev

# Production image with no dev packages nor build deps
FROM python:3.9-slim AS production

RUN set -ex \
    && apt update

ARG PROJECTDIR=api_demo_v3

EXPOSE 80

ENV PATH="/${PROJECTDIR}/.venv/bin:$PATH"
ENV PYTHONPATH="/srv/app"


COPY --from=base ./${PROJECTDIR}/.venv ./${PROJECTDIR}/.venv
COPY ./${PROJECTDIR} /srv/app

WORKDIR /srv/app

# Development image with dev packages and build deps
FROM base as development

ENV PYTHONPATH="/srv/app"

ARG PROJECTDIR=api_demo_v3

RUN set -ex \
    && apt update

WORKDIR /${PROJECTDIR}

RUN poetry install

COPY ./${PROJECTDIR} /srv/app

WORKDIR /srv/app
