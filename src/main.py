from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.logging_config import setup_logging
from src.core.exceptions import CreatorIQException
from src.middleware.logging_middleware import LoggingMiddleware
from src.api import auth, channels, trends, strategy, planner, analytics

# Initialize logging
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(channels, prefix=f"{settings.API_V1_STR}/channels", tags=["channels"])
app.include_router(trends, prefix=f"{settings.API_V1_STR}/trends", tags=["trends"])
app.include_router(strategy, prefix=f"{settings.API_V1_STR}/strategy", tags=["strategy"])
app.include_router(planner, prefix=f"{settings.API_V1_STR}/planner", tags=["planner"])
app.include_router(analytics, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])

@app.exception_handler(CreatorIQException)
async def creatoriq_exception_handler(request: Request, exc: CreatorIQException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "meta": {"request_id": getattr(request.state, "request_id", None)}
        }
    )

@app.get("/")
async def root():
    return {"message": "CreatorIQ API v1.0 is operational", "status": "healthy"}
