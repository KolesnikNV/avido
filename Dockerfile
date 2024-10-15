FROM python:3.11
WORKDIR /app

COPY avido/ .
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install -r requirements.txt

RUN chmod +x docker-entrypoint.sh