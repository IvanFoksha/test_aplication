from fastapi import FastAPI
from app.api import routers

app = FastAPI(
    title="Building and Organization Directory API",
    description="A simple API to manage buildings, organizations, and their activities.",
    version="1.0.0",
)

app.include_router(routers.router)

@app.get("/")
def read_root():
    return {"status": "ok"}
