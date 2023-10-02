FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

RUN python -m venv .venv

COPY requirements.txt .

RUN ./.venv/bin/pip install -r requirements.txt