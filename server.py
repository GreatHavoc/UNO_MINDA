"""
server.py
=========
UNO Minda Business Intelligence — FastAPI REST API Server.

Endpoints (all require X-API-Key header):
  GET /api/v1/health                — Health check (no auth required)
  GET /api/v1/company/profile       — Company overview
  GET /api/v1/company/products      — Product portfolio
  GET /api/v1/competitors           — Competitor analysis
  GET /api/v1/partnerships          — JVs and partnerships
  GET /api/v1/market-analysis       — Market analysis + SWOT
  GET /api/v1/news                  — Live UNO Minda news
  GET /api/v1/news/competitors      — Live competitor news
  GET /api/v1/stock                 — Live stock data

Run locally:
  python server.py

PythonAnywhere (ASGI via uvicorn):
  /home/USERNAME/.virtualenvs/uno_minda_venv/bin/uvicorn \
    --app-dir /home/USERNAME/uno_minda_api \
    --uds ${DOMAIN_SOCKET} \
    server:app
"""

# ---------------------------------------------------------------------------
# PATH BOOTSTRAP — must come before any local imports.
# Adds this file's own directory to sys.path so that sibling modules
# (data, config, services, security) are always importable regardless of
# how uvicorn is launched (--app-dir, PYTHONPATH, start.sh, etc.)
# ---------------------------------------------------------------------------
import sys
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import datetime
import logging
import logging.config
import os
from contextlib import asynccontextmanager
from typing import Annotated, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings, validate_settings
from data import (
    COMPETITORS,
    COMPETITOR_NEWS_TOPICS,
    MARKET_ANALYSIS,
    PARTNERSHIPS_AND_JVS,
    PRODUCT_PORTFOLIO,
    STOCK_TICKERS,
    UNO_MINDA_PROFILE,
)
from security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    verify_api_key,
)
from services import fetch_news, fetch_stock_data

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": (
                    '{"time": "%(asctime)s", "level": "%(levelname)s", '
                    '"logger": "%(name)s", "message": "%(message)s"}'
                ),
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": settings.LOG_LEVEL, "handlers": ["console"]},
    }
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-memory TTL cache
# ---------------------------------------------------------------------------

try:
    from cachetools import TTLCache
    _news_cache: TTLCache = TTLCache(maxsize=20, ttl=settings.CACHE_TTL_NEWS)
    _stock_cache: TTLCache = TTLCache(maxsize=20, ttl=settings.CACHE_TTL_STOCK)
    _CACHE_AVAILABLE = True
except ImportError:
    _CACHE_AVAILABLE = False
    _news_cache = {}   # type: ignore[assignment]
    _stock_cache = {}  # type: ignore[assignment]
    logger.warning("cachetools not installed — caching disabled")


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup validation and shutdown cleanup."""
    logger.info("Starting UNO Minda API server v%s", settings.APP_VERSION)
    try:
        validate_settings()
    except RuntimeError as exc:
        logger.critical("Configuration error: %s", exc)
        raise
    logger.info("Security validation passed. API key is set and valid length.")
    logger.info("Allowed CORS origins: %s", settings.ALLOWED_ORIGINS)
    yield
    logger.info("Server shutting down.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_TITLE,
    description=(
        settings.APP_DESCRIPTION
        + "\n\n"
        + "## Authentication\n"
        + "All endpoints (except `/api/v1/health`) require an `X-API-Key` header.\n"
        + "Click **Authorize** above and enter your API key to test endpoints here."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",      # Always available — protected by API key on data endpoints
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    # Register the API key security scheme so Swagger shows an Authorize button
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan,
)

# --- Middleware (order matters: outermost runs first on request, last on response) ---

# 1. Security headers (wraps everything)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate limiting
app.add_middleware(RateLimitMiddleware)

# 3. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type", "Accept"],
    max_age=600,
)


# ---------------------------------------------------------------------------
# OpenAPI security scheme — adds "Authorize" button to Swagger UI
# ---------------------------------------------------------------------------

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Register the API key security scheme
    schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key required for all endpoints except /api/v1/health",
        }
    }
    # Apply it globally to all paths
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            if isinstance(operation, dict):
                operation.setdefault("security", [{"ApiKeyAuth": []}])
    # Health check is public — remove security requirement from it
    health_path = schema["paths"].get("/api/v1/health", {})
    for operation in health_path.values():
        if isinstance(operation, dict):
            operation["security"] = []
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a safe error response without leaking internal details."""
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = datetime.datetime.utcnow()
    response = await call_next(request)
    duration_ms = (datetime.datetime.utcnow() - start).total_seconds() * 1000

    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else (
        request.client.host if request.client else "unknown"
    )

    logger.info(
        '{"ip": "%s", "method": "%s", "path": "%s", "status": %d, "duration_ms": %.1f}',
        ip,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Response envelope helper
# ---------------------------------------------------------------------------

def ok(data, meta: Optional[dict] = None) -> dict:
    """Wrap successful response data in a consistent envelope."""
    envelope = {
        "status": "success",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "data": data,
    }
    if meta:
        envelope["meta"] = meta
    return envelope


# ---------------------------------------------------------------------------
# Dependency type alias
# ---------------------------------------------------------------------------

AuthDep = Annotated[str, Depends(verify_api_key)]


# ===========================================================================
# ENDPOINTS
# ===========================================================================

# ---------------------------------------------------------------------------
# Health check (public — no auth required)
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/health",
    tags=["System"],
    summary="Health check",
)
async def health_check():
    """
    Returns the API server health status.
    This endpoint does NOT require an API key and can be used by uptime monitors.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }


# ---------------------------------------------------------------------------
# Company profile
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/company/profile",
    tags=["Company"],
    summary="Get UNO Minda company profile",
)
async def get_company_profile(_: AuthDep):
    """
    Returns the complete UNO Minda company overview including financials,
    headquarters, management, and key metrics.
    """
    return ok(UNO_MINDA_PROFILE)


# ---------------------------------------------------------------------------
# Product portfolio
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/company/products",
    tags=["Company"],
    summary="Get product portfolio",
)
async def get_products(
    _: AuthDep,
    category: Annotated[
        Optional[str],
        Query(description="Filter by product category name (case-insensitive, partial match)"),
    ] = None,
):
    """
    Returns the full product portfolio across all 12+ product lines.
    Optionally filter by category using the `category` query parameter.

    Example: `?category=EV` returns only EV-specific products.
    """
    if category:
        filtered = {
            k: v
            for k, v in PRODUCT_PORTFOLIO.items()
            if category.lower() in k.lower()
        }
        if not filtered:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"No product category matching '{category}'. "
                                   f"Available categories: {list(PRODUCT_PORTFOLIO.keys())}",
                    }
                },
            )
        return ok(filtered, meta={"filtered_by": category, "count": len(filtered)})

    return ok(PRODUCT_PORTFOLIO, meta={"count": len(PRODUCT_PORTFOLIO)})


# ---------------------------------------------------------------------------
# Competitors
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/competitors",
    tags=["Competitors"],
    summary="Get competitor analysis",
)
async def get_competitors(
    _: AuthDep,
    market: Annotated[
        Optional[Literal["indian", "global"]],
        Query(description="Filter by market: 'indian' or 'global'"),
    ] = None,
):
    """
    Returns competitor profiles including key products, revenue, market position,
    and areas of competition with UNO Minda.

    Filter by `?market=indian` or `?market=global`.
    """
    if market:
        data = COMPETITORS.get(market)
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_PARAMETER",
                        "message": "market must be 'indian' or 'global'",
                    }
                },
            )
        return ok(
            {market: data},
            meta={"market_filter": market, "count": len(data)},
        )

    return ok(
        COMPETITORS,
        meta={
            "indian_count": len(COMPETITORS["indian"]),
            "global_count": len(COMPETITORS["global"]),
        },
    )


# ---------------------------------------------------------------------------
# Partnerships & JVs
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/partnerships",
    tags=["Partnerships"],
    summary="Get JVs, partnerships, and strategic moves",
)
async def get_partnerships(_: AuthDep):
    """
    Returns all joint ventures (13 total), strategic partnerships,
    and recent strategic moves including the EV JV with Inovance.
    """
    return ok(PARTNERSHIPS_AND_JVS)


# ---------------------------------------------------------------------------
# Market analysis
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/market-analysis",
    tags=["Market Analysis"],
    summary="Get market analysis and SWOT",
)
async def get_market_analysis(
    _: AuthDep,
    section: Annotated[
        Optional[Literal["industry_overview", "uno_minda_market_position", "financial_summary", "swot"]],
        Query(description="Return only a specific section of the analysis"),
    ] = None,
):
    """
    Returns comprehensive market analysis including industry overview,
    UNO Minda market position, financial summary, and SWOT analysis.

    Use `?section=swot` to get only the SWOT analysis.
    """
    if section:
        data = MARKET_ANALYSIS.get(section)
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Section '{section}' not found. "
                                   f"Valid: {list(MARKET_ANALYSIS.keys())}",
                    }
                },
            )
        return ok({section: data})

    return ok(MARKET_ANALYSIS)


# ---------------------------------------------------------------------------
# Live news — UNO Minda
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/news",
    tags=["Live Data"],
    summary="Get latest UNO Minda news",
)
async def get_uno_minda_news(
    _: AuthDep,
    limit: Annotated[
        int,
        Query(ge=1, le=20, description="Number of news articles to return (1–20)"),
    ] = 10,
    fetch_articles: Annotated[
        bool,
        Query(description="If true, fetches full article content (slower)"),
    ] = False,
):
    """
    Fetches the latest news about UNO Minda from the web (via DuckDuckGo).

    - Results are cached for 5 minutes to avoid redundant external calls.
    - Set `fetch_articles=true` to include full article text (significantly slower).
    """
    cache_key = f"news:unominda:{limit}:{fetch_articles}"
    if cache_key in _news_cache:
        logger.debug("Cache hit for %s", cache_key)
        return ok(_news_cache[cache_key], meta={"cached": True})

    articles = fetch_news("UNO Minda automotive", num=limit, fetch_articles=fetch_articles)
    _news_cache[cache_key] = articles

    return ok(
        articles,
        meta={"topic": "UNO Minda", "count": len(articles), "cached": False},
    )


# ---------------------------------------------------------------------------
# Live news — Competitors
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/news/competitors",
    tags=["Live Data"],
    summary="Get latest competitor news",
)
async def get_competitor_news(
    _: AuthDep,
    company: Annotated[
        Optional[str],
        Query(
            description=(
                "Filter by company key. Available: "
                + ", ".join(f"'{v}'" for v in COMPETITOR_NEWS_TOPICS.values())
            )
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=10, description="Number of news articles per company (1–10)"),
    ] = 5,
    fetch_articles: Annotated[
        bool,
        Query(description="If true, fetches full article content (significantly slower)"),
    ] = False,
):
    """
    Fetches the latest news for each key UNO Minda competitor.

    - Results are cached for 5 minutes.
    - Filter to a single company using the `company` query parameter.
    """
    results = {}

    # Determine which topics to fetch
    topics_to_fetch = {}
    if company:
        # Find matching topic by value (company display name)
        matched = {
            k: v
            for k, v in COMPETITOR_NEWS_TOPICS.items()
            if company.lower() in v.lower()
        }
        if not matched:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": (
                            f"No competitor matching '{company}'. "
                            f"Available: {list(COMPETITOR_NEWS_TOPICS.values())}"
                        ),
                    }
                },
            )
        topics_to_fetch = matched
    else:
        topics_to_fetch = COMPETITOR_NEWS_TOPICS

    for topic, company_name in topics_to_fetch.items():
        cache_key = f"news:competitor:{topic}:{limit}:{fetch_articles}"
        if cache_key in _news_cache:
            results[company_name] = _news_cache[cache_key]
        else:
            articles = fetch_news(topic, num=limit, fetch_articles=fetch_articles)
            _news_cache[cache_key] = articles
            results[company_name] = articles

    return ok(results, meta={"companies": list(results.keys()), "limit_per_company": limit})


# ---------------------------------------------------------------------------
# Live stock data
# ---------------------------------------------------------------------------

@app.get(
    f"{settings.API_V1_PREFIX}/stock",
    tags=["Live Data"],
    summary="Get stock & financial data",
)
async def get_stock_data(
    _: AuthDep,
    ticker: Annotated[
        Optional[str],
        Query(
            description=(
                "Filter by company name. Available: "
                + ", ".join(f"'{k}'" for k in STOCK_TICKERS.keys())
            )
        ),
    ] = None,
):
    """
    Returns live stock data for UNO Minda and its Indian listed competitors.

    Data includes current price, market cap, P/E ratio, revenue (TTM),
    profit margin, and 52-week high/low.

    - Results are cached for 2 minutes.
    - Filter to a single company using the `ticker` query parameter.
    """
    tickers_to_fetch: dict[str, str] = {}

    if ticker:
        matched = {
            k: v
            for k, v in STOCK_TICKERS.items()
            if ticker.lower() in k.lower()
        }
        if not matched:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": (
                            f"No company matching '{ticker}'. "
                            f"Available: {list(STOCK_TICKERS.keys())}"
                        ),
                    }
                },
            )
        tickers_to_fetch = matched
    else:
        tickers_to_fetch = STOCK_TICKERS

    results = {}
    for company_name, ticker_symbol in tickers_to_fetch.items():
        cache_key = f"stock:{ticker_symbol}"
        if cache_key in _stock_cache:
            results[company_name] = _stock_cache[cache_key]
        else:
            data = fetch_stock_data(ticker_symbol)
            _stock_cache[cache_key] = data
            results[company_name] = data

    return ok(results, meta={"companies": list(results.keys())})


# ===========================================================================
# Entry point (local development)
# ===========================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
