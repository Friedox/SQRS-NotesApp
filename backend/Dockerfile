FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-interaction --no-root

COPY . /app

RUN poetry lock && \
    poetry install --no-interaction

EXPOSE 8000

CMD ["/bin/sh", "-c", " \
  poetry run alembic upgrade head; \
  poetry run python -m main"]
