# 🚀 Deploying UNO Minda API to PythonAnywhere

This guide walks you through deploying the UNO Minda FastAPI server to
PythonAnywhere using their ASGI (uvicorn) hosting.

---

## Prerequisites

- A PythonAnywhere account (free tier works)
- Your project files ready (this repository)

---

## Step 1 — Upload Your Project Files to PythonAnywhere

### Option A: Upload via Files tab (easiest)
1. Log into [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to **Files** tab
3. Create a new directory: `/home/YOUR_USERNAME/uno_minda_api/`
4. Upload these files into that directory:
   - `server.py`
   - `data.py`
   - `services.py`
   - `security.py`
   - `config.py`
   - `requirements.txt`
   - `.env` *(create this from `.env.example` — see Step 3)*

### Option B: Clone from GitHub (recommended for updates)
In a **Bash Console** on PythonAnywhere:
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git uno_minda_api
cd uno_minda_api
```

---

## Step 2 — Create a Virtual Environment

Open a **Bash Console** on PythonAnywhere and run:

```bash
# Create virtualenv (use Python 3.10 — stable on PythonAnywhere)
mkvirtualenv uno_minda_venv --python=python3.10

# The venv will activate automatically. Install dependencies:
pip install -r ~/uno_minda_api/requirements.txt
```

> **Note:** Installation may take 2–3 minutes. yfinance and pandas are large packages.

---

## Step 3 — Create Your .env File

In the Bash Console:

```bash
cd ~/uno_minda_api

# Copy the template
cp .env.example .env

# Edit the file (nano or vim)
nano .env
```

**Required changes in .env:**

```bash
# Generate a strong API key first:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Then paste it as your API_KEY in .env:
API_KEY=paste-your-generated-key-here

# Set allowed origins (use your domain or * for testing):
ALLOWED_ORIGINS=*

# Keep DEBUG=false in production
DEBUG=false
```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Step 4 — Install the PythonAnywhere CLI Tool

```bash
pip install --upgrade pythonanywhere
```

---

## Step 5 — Generate an API Token

1. Go to your PythonAnywhere **Account** page
2. Click the **API Token** tab
3. Click **Create a new API token**
4. The token is now stored and available to the `pa` command automatically

---

## Step 6 — Deploy the ASGI Website

In your Bash Console, run this command (replace `YOUR_USERNAME`):

```bash
pa website create \
  --domain YOUR_USERNAME.pythonanywhere.com \
  --command '/home/YOUR_USERNAME/.virtualenvs/uno_minda_venv/bin/uvicorn --app-dir /home/YOUR_USERNAME/uno_minda_api --uds ${DOMAIN_SOCKET} server:app'
```

If successful, you'll see:
```
< All done! Your site is now live at YOUR_USERNAME.pythonanywhere.com. >
```

---

## Step 7 — Verify the Deployment

Test the health endpoint (no API key needed):
```bash
curl https://YOUR_USERNAME.pythonanywhere.com/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-06-02T12:00:00Z"
}
```

Test an authenticated endpoint:
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  https://YOUR_USERNAME.pythonanywhere.com/api/v1/company/profile
```

---

## Available Endpoints

| Endpoint | Auth Required | Description |
|----------|--------------|-------------|
| `GET /api/v1/health` | ❌ No | Health check |
| `GET /api/v1/company/profile` | ✅ Yes | Company overview |
| `GET /api/v1/company/products` | ✅ Yes | Product portfolio (`?category=EV`) |
| `GET /api/v1/competitors` | ✅ Yes | Competitors (`?market=indian\|global`) |
| `GET /api/v1/partnerships` | ✅ Yes | JVs & partnerships |
| `GET /api/v1/market-analysis` | ✅ Yes | Market analysis (`?section=swot`) |
| `GET /api/v1/news` | ✅ Yes | Live news (`?limit=5&fetch_articles=true`) |
| `GET /api/v1/news/competitors` | ✅ Yes | Competitor news (`?company=Bosch`) |
| `GET /api/v1/stock` | ✅ Yes | Stock data (`?ticker=UNO+Minda`) |

---

## Reloading After Code Changes

When you update your code, reload the site:

```bash
pa website reload --domain YOUR_USERNAME.pythonanywhere.com
```

---

## Viewing Logs

```bash
# Error log (startup errors, exceptions)
cat /var/log/YOUR_USERNAME.pythonanywhere.com.error.log

# Server log (incoming requests)
cat /var/log/YOUR_USERNAME.pythonanywhere.com.server.log

# Access log (Apache-style access log)
cat /var/log/YOUR_USERNAME.pythonanywhere.com.access.log
```

---

## Updating Your Code from GitHub

```bash
cd ~/uno_minda_api
git pull origin main
pa website reload --domain YOUR_USERNAME.pythonanywhere.com
```

---

## Security Checklist

- [x] API key is set and at least 32 characters
- [x] `DEBUG=false` in production (disables Swagger UI)
- [x] `ALLOWED_ORIGINS` is set to your actual domain (not `*`) in production
- [x] `.env` file is NOT in version control (check `.gitignore`)
- [x] API key is rotated if ever exposed

---

## Example .gitignore

Make sure your `.gitignore` includes:
```
.env
__pycache__/
*.pyc
.venv/
```

---

## Testing All Endpoints (Quick Reference)

```bash
# Set your values
BASE_URL="https://YOUR_USERNAME.pythonanywhere.com"
KEY="your-api-key"

# Health (no auth)
curl "$BASE_URL/api/v1/health"

# Company profile
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/company/profile"

# Products (filtered)
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/company/products?category=EV"

# Competitors (Indian only)
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/competitors?market=indian"

# Partnerships
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/partnerships"

# Market Analysis (SWOT only)
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/market-analysis?section=swot"

# Live News (5 articles, snippets only)
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/news?limit=5"

# Competitor News (Bosch only)
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/news/competitors?company=Bosch"

# Stock Data (UNO Minda only)
curl -H "X-API-Key: $KEY" "$BASE_URL/api/v1/stock?ticker=UNO+Minda"
```
