import re
import logging
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
from flask_limiter.util import get_remote_address
import os

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# API keys array
API_KEYS = ["zzz", "yyy", "xxx"]

# API key validation
@app.before_request
def validate_api_key():
    """Validate API key in the headers."""
    api_key = request.headers.get("API-Key")
    if api_key not in API_KEYS:
        return jsonify({"error": "Invalid or missing API key"}), 403

# Helper functions
def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    pattern = r'(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-]{11})'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

def is_valid_url(url):
    """Validates if the provided URL is well-formed."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def fetch_video_data(url, include_start_times=False):
    """Fetches and formats video data, optionally including start times in the transcript."""
    try:
        api_key = os.getenv("YOUTUBE_API_KEY", "aa")
        video_id = extract_video_id(url)
        if not video_id:
            return "Invalid YouTube URL"

        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(part="snippet,statistics,contentDetails", id=video_id)
        response = request.execute()

        # Extract details
        if 'items' not in response or not response['items']:
            return {"error": "Video not found or unavailable."}

        item = response['items'][0]
        title = item['snippet']['title']
        creator = item['snippet']['channelTitle']
        description = item['snippet']['description']
        publish_date = item['snippet']['publishedAt']
        tags = item['snippet'].get('tags', [])
        category_id = item['snippet']['categoryId']
        likes = item['statistics'].get('likeCount', 'N/A')
        views = item['statistics'].get('viewCount', 'N/A')
        comments = item['statistics'].get('commentCount', 'N/A')
        duration = item['contentDetails']['duration']

        # Fetch transcript
        transcript = []
        transcript_text_only = ""
        transcript_token_count = 0
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            for entry in transcript_data:
                if include_start_times:
                    transcript.append({"start": entry['start'], "text": entry['text']})
                transcript_text_only += entry['text'] + " "
                transcript_token_count += len(entry['text'].split())
        except Exception as e:
            transcript = f"Could not fetch transcript: {e}"

        # Format data into a single string
        content = f"""
        Title: {title}
        Creator: {creator}
        Description: {description}
        Publish Date: {publish_date}
        Tags: {', '.join(tags)}
        Category ID: {category_id}
        Likes: {likes}
        Views: {views}
        Comments: {comments}
        Duration: {duration}
        Transcript Token Count: {transcript_token_count}

        Transcript:
        {transcript_text_only.strip() if not include_start_times else transcript}
        """

        return {"url": url, "content": content.strip(), "summary": f"Token count: {transcript_token_count}"}

    except Exception as e:
        return {"error": f"An error occurred: {e}"}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "The API is running properly."}), 200

@app.route('/capabilities', methods=['GET'])
def capabilities():
    return jsonify({
        "endpoints": [
            {"path": "/read_link", "method": "POST", "description": "Reads and processes a link (YouTube or webpage)."},
            {"path": "/health", "method": "GET", "description": "Checks the health of the API."},
            {"path": "/capabilities", "method": "GET", "description": "Lists all capabilities of the API."}
        ]
    }), 200

@app.route("/info", methods=["GET"])
def info():
    """General information about the server."""
    return jsonify({
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
        ],
        "about": "Belto's Link Extractor API processes YouTube links and general webpages for structured data. Licensed and maintained by Belto Inc.",
        "license": "Belto Inc. All Rights Reserved.",
        "api_key_info": "API keys are required to access this service. To request an API key, contact us at info@beltoss.com.",
        "repository": "https://github.com/BeltoAI/Belto-LinkExtractor.git"
    })

@app.route('/read_link', methods=['POST'])
def read_link():
    # Log request
    logging.info(f"Processing request: {request.json}")

    # Get the URL from the JSON body
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    url = data['url']
    if not is_valid_url(url):
        return jsonify({"error": "Invalid URL provided."}), 400

    # Check if it's a YouTube URL
    if extract_video_id(url):
        video_data = fetch_video_data(url, include_start_times=False)
        return jsonify(video_data)

    try:
        # Fallback: Fetch the content of the URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts and styles
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()

        # Extract clean text
        text_content = soup.get_text(separator=' ', strip=True)

        # Filter meaningful tags
        meaningful_text = "\n".join([tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'yt-formatted-string'])])

        # Count tokens (words)
        token_count = len(meaningful_text.split())

        # Add a summary
        summary = f"\n\nToken count: {token_count}"

        return jsonify({"url": url, "content": meaningful_text + summary, "summary": f"Token count: {token_count}"})

    except requests.exceptions.Timeout:
        return jsonify({"error": "The request timed out.", "code": 408}), 408

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Failed to connect to the server.", "code": 503}), 503

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}", "code": response.status_code}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"An error occurred while processing the request: {e}", "code": 500}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
