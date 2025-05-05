FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

RUN echo '#!/bin/sh\n\
poetry run alembic upgrade head\n\
poetry run uvicorn main:app --host 0.0.0.0 --port 8000' > /app/start.sh && \
chmod +x /app/start.sh

CMD ["/app/start.sh"]
