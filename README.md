# Link Extractor API

![Alt text](logo.png)

The Link Extractor API is a Flask-based RESTful API designed to process and extract data from YouTube videos and general webpages. It features advanced validation, token counting, and transcript fetching while ensuring secure access through API key validation.

---

## Table of Contents
1. [Features](#features)
2. [Setup](#setup)
3. [Endpoints](#endpoints)
    - [GET /health](#get-health)
    - [GET /capabilities](#get-capabilities)
    - [GET /info](#get-info)
    - [POST /read_link](#post-read_link)
4. [Usage](#usage)
5. [Dependencies](#dependencies)

---

## Features
- YouTube video data extraction (title, creator, description, views, likes, etc.).
- Webpage content extraction and token counting.
- API key validation for secure access.
- Rate-limited requests to ensure fair usage.
- Transcript fetching with token count summary.

---

## Setup

### Prerequisites
- Python 3.8+
- Install the required dependencies listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Environment Variables
Set the following environment variable:

```bash
export YOUTUBE_API_KEY="<your_youtube_api_key>"
```

### Running the API
Run the application:

```bash
python app.py
```

---

## Endpoints

### GET /health

Checks the health status of the API.

| Method | Endpoint   | Description                | Parameters | Example          |
|--------|------------|----------------------------|------------|------------------|
| GET    | `/health`  | Verifies API health status | None       | `/health`        |

#### Response Example
```json
{
  "status": "healthy",
  "message": "The API is running properly."
}
```

---

### GET /capabilities

Lists all the capabilities of the API.

| Method | Endpoint         | Description                     | Parameters | Example          |
|--------|------------------|---------------------------------|------------|------------------|
| GET    | `/capabilities`  | Lists available API endpoints. | None       | `/capabilities`  |

#### Response Example
```json
{
  "endpoints": [
    {"path": "/read_link", "method": "POST", "description": "Reads and processes a link (YouTube or webpage)."},
    {"path": "/health", "method": "GET", "description": "Checks the health of the API."},
    {"path": "/capabilities", "method": "GET", "description": "Lists all capabilities of the API."}
  ]
}
```

---

### GET /info

Provides general information about the API.

| Method | Endpoint | Description                 | Parameters | Example  |
|--------|----------|-----------------------------|------------|----------|
| GET    | `/info`  | Returns API details         | None       | `/info`  |

#### Response Example
```json
{
  "server_name": "Link Extractor API",
  "version": "1.0",
  "features": [
    "YouTube video data extraction",
    "Webpage content extraction",
    "Token and word counting",
    "Rate-limited API access",
    "API key validation"
  ],
  "developers": [
    {
      "name": "Belto Developers Team",
      "organization": "Belto Inc.",
      "contact_email": "info@beltoss.com"
    }
  ]
}
```

---

### POST /read_link

Processes a URL (YouTube or general webpage) and extracts data.

| Method | Endpoint     | Description                                         | Parameters      | Example            |
|--------|--------------|-----------------------------------------------------|-----------------|--------------------|
| POST   | `/read_link` | Extracts data from YouTube videos or general links. | `url` (required)| `/read_link`       |

#### Request Example
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

#### Response Example (YouTube)
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "content": "Title: Example Video\nCreator: Example Channel\nDescription: Example description...",
  "summary": "Token count: 500"
}
```

#### Response Example (Webpage)
```json
{
  "url": "https://example.com",
  "content": "Cleaned webpage content...",
  "summary": "Token count: 1200"
}
```

---

## Usage

### Import Required Libraries
```python
import requests

headers = {"API-Key": "<your_api_key>"}
```

### Example: Checking API Health
```python
response = requests.get("http://localhost:5001/health", headers=headers)
print(response.json())
```

### Example: Extracting Data from a URL
```python
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
response = requests.post("http://localhost:5001/read_link", headers=headers, json={"url": url})
print(response.json())
```

---

## Dependencies
Ensure all dependencies are installed as specified in `requirements.txt`. Key libraries include:

- Flask
- BeautifulSoup4
- youtube-transcript-api
- google-api-python-client
- requests

---

For detailed documentation or issues, contact `info@beltoss.com` or visit the [repository](https://github.com/BeltoAI/Belto-LinkExtractor.git).

