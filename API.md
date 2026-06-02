# 🌐 UNO Minda REST API Reference

This document provides a detailed reference for all REST API endpoints exposed by the UNO Minda Business Intelligence Server.

---

## 🔑 Authentication

All endpoints (except the health check) require a valid API key passed in the request headers.

- **Header Name**: `X-API-Key`
- **Minimum Length**: 32 characters

### Example Request in Different Environments

#### 1. curl
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/v1/company/profile
```

#### 2. Python (requests)
```python
import requests

headers = {"X-API-Key": "YOUR_API_KEY"}
response = requests.get("http://localhost:8000/api/v1/company/profile", headers=headers)
data = response.json()
print(data)
```

#### 3. JavaScript (Fetch)
```javascript
fetch('http://localhost:8000/api/v1/company/profile', {
  headers: {
    'X-API-Key': 'YOUR_API_KEY',
    'Accept': 'application/json'
  }
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 📦 JSON Response Envelope

Successful requests always return a JSON response with a consistent wrapper structure containing `status`, `timestamp`, `data` (and optional `meta` for pagination, filters, count, or caching metadata):

```json
{
  "status": "success",
  "timestamp": "2026-06-02T12:00:00.000000Z",
  "data": {
    ...
  },
  "meta": {
    ...
  }
}
```

---

## 🛑 Rate Limiting

Rate limiting is enforced based on the caller's IP address:
*   **Static Data Endpoints**: Max **60 requests/minute** per IP.
*   **Live Data Endpoints (News & Stock)**: Max **10 requests/minute** per IP (these hit external search & finance APIs, and are throttled to protect resources).

When you exceed the rate limits, the server returns a `429 Too Many Requests` status code with a `Retry-After` header.

---

## ⚡ Caching Behavior

To ensure high performance and prevent abuse of third-party APIs:
*   **Static data endpoints**: Loaded in memory and returned instantly.
*   **Live news endpoints**: Cached for **5 minutes** (300 seconds).
*   **Live stock endpoints**: Cached for **2 minutes** (120 seconds).

---

## 📂 Endpoints Reference

### 1. Health Check (Public)
*   **Endpoint**: `GET /api/v1/health`
*   **Authentication**: None
*   **Summary**: Uptime monitoring and server health verification.
*   **Example Response**:
    ```json
    {
      "status": "healthy",
      "version": "1.0.0",
      "timestamp": "2026-06-02T12:00:00.123456Z"
    }
    ```

### 2. Company Profile
*   **Endpoint**: `GET /api/v1/company/profile`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Overview of UNO Minda including founding, headquarters, management, plants, and high-level financials.
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:05:00.000000Z",
      "data": {
        "company_name": "UNO Minda Limited",
        "founded": "1958",
        "headquarters": "Gurugram, Haryana, India",
        "chairman": "N.K. Minda",
        "revenue_fy25": "INR 16,804 Crore (up 19.5% YoY)",
        "employees": "20,000+",
        "manufacturing_plants": "60+ plants across India, Indonesia, Vietnam, Mexico"
      }
    }
    ```

### 3. Product Portfolio
*   **Endpoint**: `GET /api/v1/company/products`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Returns the product lineup.
*   **Query Parameters**:
    *   `category` (string, optional): Case-insensitive partial match filter (e.g. `category=EV` or `category=switch`).
*   **Example Request**: `GET /api/v1/company/products?category=Switching`
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:06:00.000000Z",
      "data": {
        "Switching Systems": {
          "segments": ["2-Wheeler", "3-Wheeler", "4-Wheeler", "Off-road", "Commercial Vehicles"],
          "market_position": "India's #1 switch player",
          "products": ["Ignition switches", "Combination switches", "Handle bar switches"]
        }
      },
      "meta": {
        "filtered_by": "Switching",
        "count": 1
      }
    }
    ```

### 4. Competitors
*   **Endpoint**: `GET /api/v1/competitors`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Competitor profiles including key products, approximate revenues, and market positioning.
*   **Query Parameters**:
    *   `market` (string, optional): Must be exactly `indian` or `global`.
*   **Example Request**: `GET /api/v1/competitors?market=indian`
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:07:00.000000Z",
      "data": {
        "indian": {
          "Bosch Ltd (India)": {
            "headquarters": "Bengaluru, India",
            "revenue_approx": "INR 14,000+ Crore (India ops)",
            "key_products": ["Fuel injection systems", "Automotive electronics"],
            "competition_areas": ["Sensors", "Controllers", "ADAS"]
          }
        }
      },
      "meta": {
        "market_filter": "indian",
        "count": 1
      }
    }
    ```

### 5. Partnerships & JVs
*   **Endpoint**: `GET /api/v1/partnerships`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Joint ventures (13 total), technical licenses, strategic moves, and partnerships (e.g. Inovance EV JV, Toyoda Gosei).
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:08:00.000000Z",
      "data": {
        "joint_ventures": {
          "JV with Inovance Automotive (China)": {
            "entity": "Uno Minda Auto Innovations Pvt. Ltd.",
            "equity": "UNO Minda 51%, Inovance Automotive 49%",
            "products": "EV components - Electric Drive Units (EDU)",
            "status": "Active"
          }
        },
        "strategic_partnerships": { ... },
        "recent_strategic_moves": { ... }
      }
    }
    ```

### 6. Market Analysis
*   **Endpoint**: `GET /api/v1/market-analysis`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Auto component industry overview, growth drivers, SWOT, and UNO Minda financial summary.
*   **Query Parameters**:
    *   `section` (string, optional): One of `industry_overview`, `uno_minda_market_position`, `financial_summary`, or `swot`.
*   **Example Request**: `GET /api/v1/market-analysis?section=swot`
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:09:00.000000Z",
      "data": {
        "swot": {
          "strengths": ["Dominant market share in switches, horns, alloy wheels"],
          "weaknesses": ["Lower margins compared to global peers"],
          "opportunities": ["EV component market growth"],
          "threats": ["Global Tier-1s entering Indian market aggressively"]
        }
      }
    }
    ```

### 7. Live UNO Minda News
*   **Endpoint**: `GET /api/v1/news`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Live web search results for UNO Minda automotive news.
*   **Query Parameters**:
    *   `limit` (integer, optional): Number of articles to return (1-20). Default: `10`.
    *   `fetch_articles` (boolean, optional): If `true`, scrapes the full text content of each article. Slower but more comprehensive. Default: `false`.
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:10:00.000000Z",
      "data": [
        {
          "title": "Uno Minda forms joint venture with Inovance Automotive",
          "url": "https://example.com/news/123",
          "snippet": "Uno Minda has entered into a strategic joint venture...",
          "published_date": "2026-02-17"
        }
      ],
      "meta": {
        "topic": "UNO Minda",
        "count": 1,
        "cached": false
      }
    }
    ```

### 8. Live Competitor News
*   **Endpoint**: `GET /api/v1/news/competitors`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Live web news for competitors.
*   **Query Parameters**:
    *   `company` (string, optional): Filter by competitor name (e.g. `company=Bosch`).
    *   `limit` (integer, optional): Number of articles per competitor (1-10). Default: `5`.
    *   `fetch_articles` (boolean, optional): Scrape full content. Default: `false`.
*   **Example Request**: `GET /api/v1/news/competitors?company=Bosch`
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:11:00.000000Z",
      "data": {
        "Bosch Ltd (India)": [
          {
            "title": "Bosch India reports earnings for Q4",
            "url": "https://example.com/news/bosch",
            "snippet": "Bosch Limited announced its financial results today..."
          }
        ]
      },
      "meta": {
        "companies": ["Bosch Ltd (India)"],
        "limit_per_company": 5
      }
    }
    ```

### 9. Live Stock Data
*   **Endpoint**: `GET /api/v1/stock`
*   **Authentication**: Required (`X-API-Key`)
*   **Summary**: Real-time stock prices, market caps, P/E ratios, and financial metrics via yfinance.
*   **Query Parameters**:
    *   `ticker` (string, optional): Filter by company name (e.g. `ticker=Minda` or `ticker=Bosch`).
*   **Example Request**: `GET /api/v1/stock?ticker=Minda`
*   **Example Response**:
    ```json
    {
      "status": "success",
      "timestamp": "2026-06-02T12:12:00.000000Z",
      "data": {
        "UNO Minda": {
          "ticker": "UNOMINDA.NS",
          "current_price": 985.4,
          "market_cap": 56700000000,
          "pe_ratio": 58.4,
          "revenue_ttm": 168040000000,
          "profit_margin": 0.055,
          "fifty_two_week_high": 1045.0,
          "fifty_two_week_low": 620.0
        }
      },
      "meta": {
        "companies": ["UNO Minda"]
      }
    }
    ```

---

## 🚫 Error Responses

The API uses standard HTTP status codes and wraps all error payloads in a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable details explaining the error."
  }
}
```

### Common Error Codes

| HTTP Status | Code | Cause |
|-------------|------|-------|
| `401 Unauthorized` | `UNAUTHORIZED` | API key is missing, invalid, or too short. |
| `404 Not Found` | `NOT_FOUND` | The requested category, section, or company does not exist. |
| `422 Unprocessable Entity` | `INVALID_PARAMETER` | Query parameter failed validation checks (e.g., incorrect enum value). |
| `429 Too Many Requests` | `RATE_LIMIT_EXCEEDED` | Exceeded request limit per minute for the IP. |
| `500 Internal Error` | `INTERNAL_SERVER_ERROR` | An unexpected server error occurred. |
