# UNO Minda Business Intelligence CLI & REST API

A secure, performance-focused, and production-ready Python application that acts as both a CLI tool and a REST API server to query and analyze business intelligence data on **UNO Minda**, its products, competitors, partnerships, live news, and stock metrics.

---

## 🚀 Quick Start

### 1. Requirements
- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) (recommended Python package manager)

### 2. Environment Setup
Clone the repository, create a virtual environment, and install dependencies:
```bash
# Using uv (fastest)
uv venv
uv pip install -r requirements.txt

# Or using standard pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create your configuration:
```bash
cp .env.example .env
```
Edit `.env` to configure your `API_KEY` (must be at least 32 characters long) and configuration options.

---

## 💻 CLI Usage

Run the business intelligence CLI tool to query information directly in your terminal:

```bash
# Show help
python uno_minda_intelligence.py --help

# Show company profile
python uno_minda_intelligence.py --profile

# Show competitors
python uno_minda_intelligence.py --competitors

# Fetch live stock data
python uno_minda_intelligence.py --stock
```

---

## 🌐 API Server

Launch the REST API server:

```bash
uv run uvicorn server:app --reload
```

The API exposes a set of endpoints under `/api/v1` protected by an API key. 

### Swagger Documentation
Once running, interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs` (Use the **Authorize** button and input your `X-API-Key`)
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🐳 Docker Support

To run the application inside a Docker container:

```bash
# Start with Docker Compose
docker compose up --build -d
```

For more details, see [DOCKER.md](file:///c:/Users/Prakhar/Desktop/UNO_MINDA/DOCKER.md).

---

## ☁️ Deployment

For step-by-step instructions on deploying to **PythonAnywhere** without Docker, see [DEPLOY.md](file:///c:/Users/Prakhar/Desktop/UNO_MINDA/DEPLOY.md).
For deploying to containerized environments (Render, AWS, Railway, etc.), see [DOCKER.md](file:///c:/Users/Prakhar/Desktop/UNO_MINDA/DOCKER.md).
