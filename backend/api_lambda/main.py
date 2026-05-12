"""
main.py (api_lambda)

FastAPI application entry point for the API Lambda.

Critical wiring:
    handler = Mangum(app)

This module-level ``handler`` symbol is what AWS Lambda invokes.
API Gateway sends events to this adapter, which translates them into
ASGI-compatible requests that FastAPI can process.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routes.invoice_routes import router as invoice_router
from utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Invoice Analysis API",
    description=(
        "Serverless API for uploading invoices to S3 and retrieving "
        "structured invoice data extracted by AWS Textract."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — restrict in production to your actual frontend domain
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten to frontend domain in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(invoice_router, tags=["Invoices"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"], summary="Lambda health check")
def health_check() -> dict[str, str]:
    """Return a simple liveness probe response."""
    logger.info("Health check called.")
    return {"status": "healthy", "service": "ai-invoice-api"}


# ---------------------------------------------------------------------------
# Mangum adapter — THIS is the AWS Lambda entrypoint
# ---------------------------------------------------------------------------

handler = Mangum(app, lifespan="off")
