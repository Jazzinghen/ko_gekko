# syntax=docker/dockerfile:1
FROM python:3.10-bullseye

# Disable root warnings for PIP and use Pipenv in folders
ENV PIPENV_VENV_IN_PROJECT 1
ENV PIP_ROOT_USER_ACTION ignore

# Install environment tools to handle.
# It's not super good practice to not provide versions when using pip install,
# but this is a "meta-call" since we are upgrading pip to the latest version
# and installing the most recent pipenv for security reasons
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv

# Create environment
RUN ["mkdir", "-p", "/opt/ko_gekko/downloads"]
WORKDIR /opt/ko_gekko

# Setup application
COPY . .
RUN pipenv install
