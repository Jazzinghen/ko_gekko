# syntax=docker/dockerfile:1
FROM python:3.10-bullseye

ENV PIPENV_VENV_IN_PROJECT 1
ENV PIP_ROOT_USER_ACTION ignore

# Install environment tools to handle
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv

RUN ["mkdir", "-p", "/opt/ko_gekko/downloads"]
WORKDIR /opt/ko_gekko

COPY . .
RUN pipenv install
