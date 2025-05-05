FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

COPY . .

RUN poetry install --no-interaction

ENV CONFIG__RUN__HOST=0.0.0.0
ENV CONFIG__RUN__PORT=8000
ENV CONFIG__RUN__DEBUG=False
ENV CONFIG__DATABASE__DB_URL=sqlite+aiosqlite:///data/notes.sqlite3

# Create data directory for SQLite database
RUN mkdir -p /app/data

EXPOSE 8000

# Create a shell script to run migrations and start the application
RUN echo '#!/bin/sh\n\
poetry run alembic upgrade head\n\
poetry run uvicorn main:app --host 0.0.0.0 --port 8000' > /app/start.sh && \
chmod +x /app/start.sh

CMD ["/app/start.sh"]
