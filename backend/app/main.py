from fastapi import FastAPI


app = FastAPI(
    title="Simple Notes API",
    description="Простой API для заметок с использованием FastAPI и SQLite",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Simple Notes API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
