from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

from app.api import routers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path}")
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Response status: {response.status_code} | "
            f"Process time: {process_time:.4f}s"
        )
        return response


app = FastAPI(
    title="Building and Organization Directory API",
    description=(
        "A simple API to manage buildings, "
        "organizations, and their activities."
    ),
    version="1.0.0",
)

# Add middlewares
app.add_middleware(LoggingMiddleware)


# Custom exception handler for unexpected errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unexpected error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Service is temporarily unavailable. "
            "Please try again later."
        },
    )

app.include_router(routers.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")


@app.get("/")
def read_root():
    return {"status": "ok"}
