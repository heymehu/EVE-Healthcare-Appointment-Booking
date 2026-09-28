import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import Base, engine, ensure_schema
from app.core.rate_limiter import setup_rate_limiter, combined_lifespan
from app.models import Booking, DiagnosticCentre, DiagnosticTest, Payment, User  # noqa: F401
from app.routers.auth import router as auth_router
from app.routers.bookings import router as bookings_router
from app.routers.centres import router as centres_router
from app.routers.payments import router as payments_router
from app.routers.tests import centres_tests_router, tests_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("eve")


settings = get_settings()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="EVE Healthcare diagnostic test booking API",
    version="1.0.0",
    lifespan=combined_lifespan,
)

setup_rate_limiter(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(centres_router)
app.include_router(centres_tests_router)
app.include_router(tests_router)
app.include_router(bookings_router)
app.include_router(payments_router)