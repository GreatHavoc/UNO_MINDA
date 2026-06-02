"""
config.py
=========
Centralised configuration loaded from environment variables / .env file.
All sensitive values (API keys, allowed origins) must be set via environment variables.
"""

import os

# Load .env from the same directory as this file — works regardless of CWD.
# This fixes the [Errno 2] No such file or directory warnings on PythonAnywhere.
try:
    from dotenv import load_dotenv
    _ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(_ENV_PATH)
except ImportError:
    pass  # python-dotenv not installed; rely on real environment variables


class Settings:
    """
    Application settings loaded from environment variables.
    Provide defaults only for non-sensitive configuration.
    """

    # -------------------------------------------------------------------------
    # Security
    # -------------------------------------------------------------------------
    # A strong, randomly generated API key. REQUIRED — server refuses to start if missing.
    API_KEY: str = os.environ.get("API_KEY", "")

    # Comma-separated list of allowed CORS origins.
    # Example: "https://myapp.com,https://staging.myapp.com"
    # Use "*" only in development; never in production.
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",")
        if o.strip()
    ]

    # -------------------------------------------------------------------------
    # Rate Limiting
    # -------------------------------------------------------------------------
    # Max requests per minute for static data endpoints (per IP)
    RATE_LIMIT_STATIC: str = os.environ.get("RATE_LIMIT_STATIC", "60/minute")
    # Max requests per minute for live data endpoints (per IP) — lower because
    # these hit external services (DuckDuckGo, yfinance)
    RATE_LIMIT_LIVE: str = os.environ.get("RATE_LIMIT_LIVE", "10/minute")

    # -------------------------------------------------------------------------
    # Cache TTLs (seconds)
    # -------------------------------------------------------------------------
    CACHE_TTL_NEWS: int = int(os.environ.get("CACHE_TTL_NEWS", "300"))    # 5 minutes
    CACHE_TTL_STOCK: int = int(os.environ.get("CACHE_TTL_STOCK", "120"))  # 2 minutes

    # -------------------------------------------------------------------------
    # Server
    # -------------------------------------------------------------------------
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO").upper()

    # -------------------------------------------------------------------------
    # Application metadata
    # -------------------------------------------------------------------------
    APP_TITLE: str = "UNO Minda Business Intelligence API"
    APP_DESCRIPTION: str = (
        "Secure REST API for UNO Minda company intelligence data including "
        "company profile, product portfolio, competitors, partnerships, "
        "market analysis, live news, and stock data."
    )
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()


def validate_settings() -> None:
    """
    Validate critical settings at startup.
    Raises RuntimeError if required settings are missing.
    """
    if not settings.API_KEY:
        raise RuntimeError(
            "API_KEY environment variable is not set. "
            "Generate a strong key and set it before starting the server. "
            "Example: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    if len(settings.API_KEY) < 32:
        raise RuntimeError(
            "API_KEY is too short (minimum 32 characters). "
            "Use a cryptographically secure random key."
        )
