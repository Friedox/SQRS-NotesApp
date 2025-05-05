FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction

COPY app/ ./app/

EXPOSE 8000

CMD ["/bin/sh", "-c", " \
  poetry run alembic upgrade head; \
  poetry run python -m main"]
